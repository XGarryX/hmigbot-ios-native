"""ObjC declarations retain state without promoting lexical observations to AST proof."""
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(os.environ.get('HMIGBOT_TEST_RUNTIME', Path(__file__).resolve().parents[1])).resolve()
sys.path.insert(0, str(ROOT / 'src'))
from hmigbot_ios.ios_facts import extract, obligations


def graph_for(files):
    with tempfile.TemporaryDirectory() as root:
        source = Path(root)
        for name, text in files.items():
            (source / name).write_text(text, encoding='utf-8')
        return extract(source)


def states(graph):
    return [f for f in graph['facts'] if f['kind'] == 'state']


class ObjCStateFactsTests(unittest.TestCase):
    def test_property_owner_type_and_reference_attributes(self):
        graph = graph_for({'Reader.h': '''@interface Reader : NSObject
@property (nonatomic, copy) NSString *filePath;
@property (nonatomic, strong) NSArray<NSString *> *pages;
@property (nonatomic, weak, nullable) id<ReaderDelegate> delegate;
@end
'''})
        found = {f['symbol']: f for f in states(graph)}
        self.assertEqual(set(found), {'filePath', 'pages', 'delegate'})
        self.assertEqual(found['filePath']['owner'], 'Reader')
        self.assertEqual(found['filePath']['value']['storage'], 'objc_property')
        self.assertEqual(found['filePath']['value']['type'], 'NSString *')
        self.assertEqual(found['filePath']['value']['ownership'], 'copy')
        self.assertEqual(found['pages']['value']['ownership'], 'strong')
        self.assertEqual(found['delegate']['value']['ownership'], 'weak')
        self.assertIn('nullable', found['delegate']['value']['attributes'])
        self.assertTrue(all(f['resolution'] == 'token_signal' for f in found.values()))

    def test_instance_ivars_retain_nil_bool_and_numeric_defaults(self):
        graph = graph_for({'Reader.m': '''@interface Reader : NSObject {
@private
 NSString *_document;
 BOOL _ready;
 int _currentPage;
 void *_buffer;
}
@end
'''})
        found = {f['symbol']: f for f in states(graph)}
        self.assertEqual({k: f['value']['initializer'] for k, f in found.items()},
                         {'_document': 'nil', '_ready': 'NO', '_currentPage': '0', '_buffer': 'NULL'})
        self.assertTrue(all(f['value']['storage'] == 'objc_ivar' for f in found.values()))
        self.assertTrue(all(f['owner'] == 'Reader' for f in found.values()))

    def test_lifecycle_assignments_do_not_replace_allocation_initial_value(self):
        graph = graph_for({'Reader.m': '''@interface Reader () {
 int _currentPage;
 BOOL _ready;
}
@property (nonatomic, strong) UIView *content;
@end
@implementation Reader
- (void)viewDidLoad {
 _currentPage = 1;
 _ready = YES;
 self.content = [[UIView alloc] init];
 self.content.hidden = NO;
}
@end
'''})
        found = {f['symbol']: f for f in states(graph)}
        self.assertIn('_currentPage', found)
        self.assertEqual(found['_currentPage']['value']['initializer'], '0')
        assignment = found['_currentPage']['value']['assignments'][0]
        self.assertEqual(assignment['expression'], '1')
        self.assertEqual(assignment['method'], 'viewDidLoad')
        self.assertEqual(assignment['phase'], 'lifecycle')
        self.assertEqual(assignment['path'], 'Reader.m')
        self.assertEqual(assignment['line'], 9)
        self.assertEqual(len(found['content']['value']['assignments']), 1)

    def test_cross_file_declarations_bind_only_own_class_receiver(self):
        graph = graph_for({'Reader.h': '''@interface Reader : NSObject
@property (copy) NSString *filePath;
@end
''', 'Reader.m': '''@implementation Reader
- (id)init {
 if ((self = [super init])) { _filePath = @"sample.ofd"; }
 return self;
}
- (void)reset { self.filePath = nil; other.filePath = @"foreign"; }
@end
@implementation Other
- (void)reset { self.filePath = @"wrong class"; }
@end
'''})
        found = states(graph)
        self.assertEqual(len(found), 1)
        self.assertEqual([a['expression'] for a in found[0]['value']['assignments']], ['@ "sample.ofd"', 'nil'])
        self.assertEqual(found[0]['value']['assignments'][0]['phase'], 'initializer')

    def test_comments_strings_locals_parameters_and_protocols_are_not_state(self):
        graph = graph_for({'Reader.m': '''// @property (strong) NSString *fake;
@protocol Contract
@property (strong) NSString *requirement;
@end
@interface Reader : NSObject
@property (strong) NSString *real;
- (void)take:(NSString *)parameter;
@end
@implementation Reader
- (void)take:(NSString *)parameter {
 NSString *local = @"@property (strong) NSString *text;";
 int _fake = 1;
}
@end
'''})
        self.assertEqual([f['symbol'] for f in states(graph)], ['real'])

    def test_shadowed_ivar_local_is_not_bound_to_instance(self):
        graph = graph_for({'Reader.m': '''@interface Reader : NSObject { int _count; }
@end
@implementation Reader
- (void)take:(int)_count { _count = 9; self->_count = 3; }
- (void)reset { int _count = 7; _count = 8; }
@end
'''})
        found = states(graph)
        self.assertEqual(len(found), 1)
        self.assertEqual([a['expression'] for a in found[0]['value']['assignments']], ['3'])

    def test_class_methods_cannot_write_instance_backing_state(self):
        graph = graph_for({'Reader.m': '''@interface Reader : NSObject { int _count; }
@end
@implementation Reader
+ (void)reset { self.count = 2; _count = 3; }
- (void)reset { _count = 4; }
@end
'''})
        self.assertEqual(len(states(graph)), 1)
        self.assertEqual([a['expression'] for a in states(graph)[0]['value']['assignments']], ['4'])

    def test_dynamic_class_and_computed_properties_keep_storage_unresolved(self):
        graph = graph_for({'Reader.m': '''@interface Reader : NSObject
@property (class, strong) NSString *shared;
@property (readonly) int computed;
@property (strong) NSString *dynamicName;
@end
@implementation Reader
@dynamic dynamicName;
- (int)computed { return 7; }
@end
'''})
        found = {f['symbol']: f for f in states(graph)}
        self.assertEqual(set(found), {'shared', 'computed', 'dynamicName'})
        self.assertTrue(all(f['value']['initializer'] is None for f in found.values()))
        self.assertTrue(all(f['value']['storage_binding'] == 'unresolved' for f in found.values()))

    def test_named_category_does_not_claim_automatic_instance_storage(self):
        graph = graph_for({'Reader.m': '''@interface Reader (Extra)
@property (strong) NSString *extra;
@end
@implementation Reader (Extra)
- (NSString *)extra { return @"x"; }
@end
'''})
        found = states(graph)
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]['value']['storage_binding'], 'unresolved')
        self.assertIsNone(found[0]['value']['initializer'])

    def test_explicit_synthesize_alias_retains_assignment_and_ownership(self):
        graph = graph_for({'Reader.m': '''@interface Reader : NSObject { NSString *_legacy; }
@property (copy) NSString *name;
@end
@implementation Reader
@synthesize name = _legacy;
- (id)init { if ((self = [super init])) { _legacy = @"first"; } return self; }
@end
'''})
        found = {f['symbol']: f for f in states(graph)}
        self.assertIn('name', found)
        self.assertEqual(found['name']['value']['backing_ivar'], '_legacy')
        self.assertEqual(found['name']['value']['ownership'], 'copy')
        self.assertEqual(found['name']['value']['assignments'], found['_legacy']['value']['assignments'])

    def test_multiple_ivars_are_parsed_but_unknown_typedef_stays_unresolved(self):
        graph = graph_for({'Reader.mm': '''@implementation Reader {
 int _first, _second;
 UnknownCount _third;
}
@end
'''})
        found = {f['symbol']: f for f in states(graph)}
        self.assertEqual(set(found), {'_first', '_second', '_third'})
        self.assertEqual(found['_second']['value']['type'], 'int')
        self.assertIsNone(found['_third']['value']['initializer'])

    def test_complex_declarators_are_diagnosed_instead_of_inventing_names(self):
        graph = graph_for({'Reader.m': '''@interface Reader : NSObject {
 int (*_callback)(int);
}
@end
'''})
        self.assertFalse(states(graph))
        self.assertIn('IOS.OBJC_STATE_UNRESOLVED', [i['rule'] for i in graph['issues']])

    def test_state_id_stable_across_comment_movement_and_obligation_exists(self):
        code = '@interface Reader : NSObject { int _page; }\n@end\n'
        first = graph_for({'Reader.m': code})
        second = graph_for({'Reader.m': '// shifted\n' + code})
        self.assertEqual(len(states(first)), 1)
        self.assertEqual(states(first)[0]['id'], states(second)[0]['id'])
        self.assertNotEqual(first['source_sha256'], second['source_sha256'])
        state_obs = [o for o in obligations(first)['obligations'] if o['kind'] == 'state']
        self.assertEqual(len(state_obs), 1)
        self.assertEqual(state_obs[0]['fact_id'], states(first)[0]['id'])
        self.assertEqual(state_obs[0]['judgments'], ['unit', 'ui'])

    def test_custom_empty_setter_does_not_imply_automatic_backing_storage(self):
        graph = graph_for({'Reader.m': '''@interface Reader : NSObject
@property (assign) BOOL ready;
@end
@implementation Reader
- (BOOL)ready { return YES; }
- (void)setReady:(BOOL)value {}
@end
'''})
        self.assertEqual(len(states(graph)), 1)
        self.assertEqual(states(graph)[0]['value']['storage_binding'], 'unresolved')
        self.assertIsNone(states(graph)[0]['value']['initializer'])

    def test_object_generics_do_not_change_outer_pointer_default(self):
        graph = graph_for({'Reader.m': '''@interface Reader : NSObject {
 NSArray<NSString *> *_names;
}
@end
'''})
        self.assertEqual(len(states(graph)), 1)
        self.assertEqual(states(graph)[0]['value']['initializer'], 'nil')

    def test_preprocessor_directives_cannot_be_an_ivar_type(self):
        graph = graph_for({'Reader.m': '''@interface Reader : NSObject {
#define FAKE_TYPE unsigned
 FAKE_TYPE _number;
}
@end
'''})
        self.assertFalse(states(graph))
        self.assertIn('IOS.OBJC_STATE_UNRESOLVED', [i['rule'] for i in graph['issues']])

    def test_selected_active_tokens_only_emit_active_ivar_and_assignment(self):
        from hmigbot_ios.objc_state import extract_states
        from hmigbot_ios.swiftui import tokenize
        code = '''@interface Reader : NSObject {
 int _active;
 int _inactive;
}
@end
@implementation Reader
- (void)reset { _active = 3; }
- (void)hidden { _inactive = 4; }
@end
'''
        tokens = [t for t in tokenize(code) if t.line not in {3, 8}]
        result, issues = extract_states([({'path': 'Reader.m'}, tokens, [{'unit': 'Reader.m', 'instance': 0}])])
        self.assertFalse(issues)
        self.assertEqual([d['symbol'] for d in result], ['_active'])
        self.assertEqual([a['expression'] for a in result[0]['value']['assignments']], ['3'])
        self.assertEqual(result[0]['contexts'], [{'unit': 'Reader.m', 'instance': 0}])

    def test_different_conditional_units_do_not_share_assignments(self):
        from hmigbot_ios.objc_state import extract_states
        from hmigbot_ios.swiftui import tokenize
        inputs = [({'path': 'Reader.h'}, tokenize('@interface Reader { int _page; }\n@end'),
                   [{'unit': 'A.m', 'instance': 0}]),
                  ({'path': 'B.m'}, tokenize('@implementation Reader\n- (void)reset { _page = 9; }\n@end'),
                   [{'unit': 'B.m', 'instance': 0}])]
        result, issues = extract_states(inputs)
        self.assertFalse(issues)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['value']['assignments'], [])

    def test_unrelated_conditional_implementation_cannot_imply_property_storage(self):
        from hmigbot_ios.objc_state import extract_states
        from hmigbot_ios.swiftui import tokenize
        inputs = [({'path': 'Reader.h'}, tokenize('@interface Reader\n@property int page;\n@end'),
                   [{'unit': 'A.m', 'instance': 0}]),
                  ({'path': 'B.m'}, tokenize('@implementation Reader\n@end'),
                   [{'unit': 'B.m', 'instance': 0}])]
        result, issues = extract_states(inputs)
        self.assertFalse(issues)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['value']['storage_binding'], 'unresolved')
        self.assertIsNone(result[0]['value']['initializer'])

    def test_block_property_preserves_return_and_parameter_types_without_making_parameters_state(self):
        graph = graph_for({'Maker.h': '''@interface Maker : NSObject
@property (nonatomic, strong, readonly) MASConstraint *(^attributes)(MASAttribute attrs);
@property (nonatomic, strong, readonly) MASViewAttribute *(^mas_attribute)(NSLayoutAttribute attr);
@end
'''})
        found = {f['symbol']: f for f in states(graph)}
        self.assertEqual(set(found), {'attributes', 'mas_attribute'})
        self.assertEqual(found['attributes']['value']['type'], 'MASConstraint * ( ^ ) ( MASAttribute attrs )')
        self.assertEqual(found['mas_attribute']['value']['type'], 'MASViewAttribute * ( ^ ) ( NSLayoutAttribute attr )')
        self.assertTrue(all(f['value']['initializer'] is None for f in found.values()))
        self.assertFalse([i for i in graph['issues'] if i['rule'] == 'IOS.OBJC_STATE_UNRESOLVED'])

    def test_balanced_api_available_tail_preserves_annotation_and_name(self):
        graph = graph_for({'View.h': '''@interface View : NSObject
@property (nonatomic, strong, readonly) MASViewAttribute *safeArea API_AVAILABLE(ios(11.0),tvos(11.0));
@end
'''})
        self.assertEqual(len(states(graph)), 1)
        state = states(graph)[0]
        self.assertEqual(state['symbol'], 'safeArea')
        self.assertEqual(state['value']['type'], 'MASViewAttribute *')
        self.assertEqual(state['value']['annotations'], ['API_AVAILABLE ( ios ( 11.0 ) , tvos ( 11.0 ) )'])
        self.assertIsNone(state['value']['initializer'])

    def test_unknown_or_unbalanced_property_annotations_are_diagnosed(self):
        for declaration in ['NSString *name UNKNOWN_API(ios(11.0))',
                            'NSString *name UNKNOWN_MARKER',
                            'NSString *name API_AVAILABLE(ios(11.0)']:
            with self.subTest(declaration=declaration):
                graph = graph_for({'View.h': '@interface View : NSObject\n@property (copy) '+declaration+';\n@end\n'})
                self.assertFalse(states(graph))
                self.assertIn('IOS.OBJC_STATE_UNRESOLVED', [i['rule'] for i in graph['issues']])

    def test_custom_accessor_attribute_selectors_are_normalized_from_tokens(self):
        for attributes in ['getter=isReady, setter=markReady:',
                           'getter = isReady, setter = markReady :',
                           'getter\n=\nisReady, setter\n=\nmarkReady\n:']:
            with self.subTest(attributes=attributes):
                graph = graph_for({'Counter.m': '''@interface Counter : NSObject
@property (''' + attributes + ''') int ready;
@end
@implementation Counter
- (int)isReady { return 1; }
- (void)markReady:(int)value {}
@end
'''})
                self.assertEqual(len(states(graph)), 1)
                self.assertEqual(states(graph)[0]['value']['storage_binding'], 'unresolved')
                self.assertIsNone(states(graph)[0]['value']['backing_ivar'])
                self.assertIsNone(states(graph)[0]['value']['initializer'])

    def test_nested_local_self_shadow_does_not_bind_other_instance_writes(self):
        graph = graph_for({'Counter.m': '''@interface Counter : NSObject { int _count; }
@property int count;
@end
@implementation Counter
- (void)reset {
 { Counter *self = (Counter *)0; self->_count = 7; self.count = 8; }
}
@end
'''})
        self.assertEqual(len(states(graph)), 2)
        self.assertTrue(all(f['value']['assignments'] == [] for f in states(graph)))

    def test_self_parameter_shadow_does_not_bind_instance_writes(self):
        graph = graph_for({'Counter.m': '''@interface Counter : NSObject { int _count; }
@property int count;
@end
@implementation Counter
- (void)reset:(Counter *)self { self->_count = 7; self.count = 8; }
@end
'''})
        self.assertEqual(len(states(graph)), 2)
        self.assertTrue(all(f['value']['assignments'] == [] for f in states(graph)))

    def test_initializing_self_is_not_a_local_self_declaration(self):
        graph = graph_for({'Counter.m': '''@interface Counter : NSObject { int _count; }
@end
@implementation Counter
- (id)init { if ((self = [super init])) { self->_count = 7; } return self; }
@end
'''})
        self.assertEqual(len(states(graph)), 1)
        self.assertEqual([a['expression'] for a in states(graph)[0]['value']['assignments']], ['7'])

    def test_unknown_property_attribute_macro_is_not_guessed_as_instance_storage(self):
        graph = graph_for({'Counter.m': '''#define PROP_FLAGS class, nonatomic
@interface Counter : NSObject
@property (PROP_FLAGS) int count;
@end
@implementation Counter
+ (int)count { return 1; }
+ (void)setCount:(int)value {}
@end
'''})
        self.assertFalse(states(graph))
        findings = [i for i in graph['issues'] if i['rule'] == 'IOS.OBJC_STATE_UNRESOLVED']
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]['path'], 'Counter.m')
        self.assertEqual(findings[0]['line'], 3)

    def test_malformed_accessor_property_attributes_are_diagnosed(self):
        for attributes in ['getter', 'getter=', 'getter=ready:', 'setter', 'setter=',
                           'setter=markReady', 'setter=markReady::', 'getter=(ready)',
                           'nonatomic, UNKNOWN_FLAGS', 'copy,,nonatomic']:
            with self.subTest(attributes=attributes):
                graph = graph_for({'Counter.m': '@interface Counter : NSObject\n@property ('+attributes+') int ready;\n@end\n'})
                self.assertFalse(states(graph))
                self.assertIn('IOS.OBJC_STATE_UNRESOLVED', [i['rule'] for i in graph['issues']])

    def test_standard_property_attribute_combinations_are_preserved(self):
        graph = graph_for({'Counter.h': '''@interface Counter : NSObject
@property (class, nonatomic, readonly, getter=current) int count;
@property (nonatomic, copy, nullable) NSString *name;
@property (atomic, strong, nonnull) NSObject *value;
@property (nonatomic, weak, null_resettable, getter=currentDelegate, setter=replaceDelegate:) id delegate;
@end
'''})
        found = {f['symbol']: f for f in states(graph)}
        self.assertEqual(set(found), {'count', 'name', 'value', 'delegate'})
        self.assertEqual(found['count']['value']['attributes'], ['class', 'nonatomic', 'readonly', 'getter = current'])
        self.assertEqual(found['name']['value']['ownership'], 'copy')
        self.assertEqual(found['value']['value']['ownership'], 'strong')
        self.assertEqual(found['delegate']['value']['ownership'], 'weak')
        self.assertFalse([i for i in graph['issues'] if i['rule'] == 'IOS.OBJC_STATE_UNRESOLVED'])

    def test_typeof_local_self_shadow_does_not_bind_another_instance(self):
        graph = graph_for({'Counter.m': '''@interface Counter : NSObject { int _count; }
@property int count;
@end
@implementation Counter
- (void)reset {
 { __typeof__(self) self = (Counter *)0; self->_count = 7; self.count = 8; }
}
@end
'''})
        self.assertEqual(len(states(graph)), 2)
        self.assertTrue(all(f['value']['assignments'] == [] for f in states(graph)))

    def test_untyped_self_parameter_does_not_bind_instance_writes(self):
        graph = graph_for({'Counter.m': '''@interface Counter : NSObject { int _count; }
@property int count;
@end
@implementation Counter
- (void)reset:self { self->_count = 7; self.count = 8; }
@end
'''})
        self.assertEqual(len(states(graph)), 2)
        self.assertTrue(all(f['value']['assignments'] == [] for f in states(graph)))

    def test_character_literals_fail_closed_without_inventing_assignment_boundaries(self):
        for assignments in ["_count = '{'; _count = '}'; _count = 3;",
                            r"_count = '\n';", r"_count = '\'';", "_count = L'{';",
                            "_count = 'unterminated;"]:
            with self.subTest(assignments=assignments):
                graph = graph_for({'Counter.m': '''@interface Counter : NSObject { int _count; }
@end
@implementation Counter
- (void)reset { '''+assignments+''' }
@end
'''})
                self.assertFalse(states(graph))
                issues = [i for i in graph['issues'] if i['rule'] == 'IOS.OBJC_STATE_UNRESOLVED']
                self.assertEqual(len(issues), 1)
                self.assertEqual(issues[0]['path'], 'Counter.m')
                self.assertEqual(issues[0]['line'], 4)

    def test_single_quotes_in_comments_and_strings_are_not_character_tokens(self):
        graph = graph_for({'Counter.m': '''// Characters '{' and '}' here are documentation.
@interface Counter : NSObject { int _count; }
@end
@implementation Counter
- (void)reset {
 NSString *message = @"it's a '{' character";
 /* _count = '{'; */
 _count = 3;
}
@end
'''})
        self.assertEqual(len(states(graph)), 1)
        self.assertEqual([a['expression'] for a in states(graph)[0]['value']['assignments']], ['3'])
        self.assertFalse([i for i in graph['issues'] if i['rule'] == 'IOS.OBJC_STATE_UNRESOLVED'])


if __name__ == '__main__':
    unittest.main()
