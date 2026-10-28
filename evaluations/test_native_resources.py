import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from hmigbot_ios152.source import Source
from hmigbot_ios152.native_resources import selected


class NativeResourceScope(unittest.TestCase):
    def test_unselected_product_resources_are_excluded(self):
        with tempfile.TemporaryDirectory() as tmp:
            src=Path(tmp)/'source';src.mkdir();project=Path(tmp)/'target';(project/'.migbot').mkdir(parents=True)
            objects={
                'P':{'isa':'PBXProject','mainGroup':'G','projectDirPath':'','targets':['T1','T2'],'buildConfigurationList':'CL'},
                'G':{'isa':'PBXGroup','sourceTree':'<group>','children':['F1','F2','R1','R2','L1','L2','J1','J2']},
                'CL':{'isa':'XCConfigurationList','buildConfigurations':['C']},
                'C':{'isa':'XCBuildConfiguration','name':'Release','buildSettings':{}},
            }
            for n in ('1','2'):
                objects['T'+n]={'isa':'PBXNativeTarget','name':'App'+n,'productType':'com.apple.product-type.application',
                                'buildConfigurationList':'CL','buildPhases':['S'+n,'R'+n+'P'],'dependencies':[]}
                objects['S'+n]={'isa':'PBXSourcesBuildPhase','files':['B'+n]}
                objects['B'+n]={'isa':'PBXBuildFile','fileRef':'F'+n}
                objects['F'+n]={'isa':'PBXFileReference','sourceTree':'<group>','path':'App'+n+'.swift'}
                objects['R'+n+'P']={'isa':'PBXResourcesBuildPhase','files':['RB'+n,'LB'+n,'JB'+n]}
                objects['RB'+n]={'isa':'PBXBuildFile','fileRef':'R'+n}
                objects['JB'+n]={'isa':'PBXBuildFile','fileRef':'J'+n}
                objects['J'+n]={'isa':'PBXFileReference','sourceTree':'<group>','path':'App'+n+'.json'}
                (src/('App'+n+'.json')).write_text(json.dumps({'label':'Resource text '+n}))
                objects['LB'+n]={'isa':'PBXBuildFile','fileRef':'L'+n}
                objects['R'+n]={'isa':'PBXFileReference','sourceTree':'<group>','path':'App'+n+'.storyboard'}
                objects['L'+n]={'isa':'PBXFileReference','sourceTree':'<group>','path':'App'+n+'.xcstrings'}
                (src/('App'+n+'.swift')).write_text('import SwiftUI\nstruct Screen'+n+': View { var body: some View { Text("Screen") } }')
                (src/('App'+n+'.storyboard')).write_text('<document><viewController id="'+n+'" customClass="Screen'+n+'"/></document>')
                (src/('App'+n+'.xcstrings')).write_text(json.dumps({'strings':{'key'+n:{}}}))
            pbx=src/'Neutral.xcodeproj/project.pbxproj';pbx.parent.mkdir()
            pbx.write_text(json.dumps({'objects':objects,'rootObject':'P'}))
            variant={'scope':'project-targets','project_path':'Neutral.xcodeproj/project.pbxproj','targets':['App1'],'configuration':'Release'}
            (project/'.migbot/config.json').write_text(json.dumps({'source_platform':'ios','ios':{'source_root':str(src),'variant':variant}}))
            source=Source(src,project)
            self.assertEqual({'App1.swift'},source.files)
            result=selected(source)
            self.assertEqual(['App1.storyboard','App1.xcstrings'],result['files'])
            self.assertEqual({'App2.storyboard','App2.xcstrings'},{x['file'] for x in result['excluded']})
            self.assertEqual('selected-product-targets',result['scope'])
            before_records=dict(source.records)
            text=selected(source,text_resources=True)
            self.assertIn('App1.json',text['files']);self.assertNotIn('App2.json',text['files'])
            self.assertEqual(['App1'],text['owners']['App1.json'])
            self.assertEqual(result,selected(source))
            self.assertEqual(before_records,source.records)  # optional scope leaves earlier Source contract intact


if __name__ == '__main__': unittest.main()
