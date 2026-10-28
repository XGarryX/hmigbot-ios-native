import Foundation
import ImageIO
import CoreGraphics

do {
    guard CommandLine.arguments.count == 2 else { throw NSError(domain:"ImageInspect",code:1) }
    let url = URL(fileURLWithPath: CommandLine.arguments[1])
    guard let source = CGImageSourceCreateWithURL(url as CFURL, nil),
          let image = CGImageSourceCreateImageAtIndex(source, 0, nil),
          image.width > 0, image.height > 0 else { throw NSError(domain:"ImageInspect",code:2) }
    let side = 64
    var pixels = [UInt8](repeating:0, count:side*side*4)
    let valid = pixels.withUnsafeMutableBytes { bytes -> Bool in
        guard let context = CGContext(data:bytes.baseAddress,width:side,height:side,bitsPerComponent:8,
            bytesPerRow:side*4,space:CGColorSpaceCreateDeviceRGB(),
            bitmapInfo:CGImageAlphaInfo.premultipliedLast.rawValue | CGBitmapInfo.byteOrder32Big.rawValue)
        else { return false }
        context.interpolationQuality = .none
        context.draw(image,in:CGRect(x:0,y:0,width:side,height:side))
        return true
    }
    guard valid else { throw NSError(domain:"ImageInspect",code:3) }
    var darkest = 255, brightest = 0, sum = 0
    for i in stride(from:0,to:pixels.count,by:4) {
        for j in 0..<3 { let c = Int(pixels[i+j]); darkest=min(darkest,c);brightest=max(brightest,c);sum+=c }
    }
    let value: [String:Any] = ["provider":"Apple ImageIO/CoreGraphics", "decoded":true,
        "width":image.width,"height":image.height,"sample_size":side,
        "sample_min":darkest,"sample_max":brightest,"sample_mean":Double(sum)/Double(side*side*3),
        "uniform_sample":darkest==brightest,"black_sample":brightest<=1]
    FileHandle.standardOutput.write(try JSONSerialization.data(withJSONObject:value,options:[.sortedKeys]))
} catch {
    FileHandle.standardError.write(Data("ImageIO decode failed: \(error)\n".utf8));exit(2)
}
