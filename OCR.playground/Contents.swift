import Vision
import VisionKit
import UIKit

var output: [String] = []

func ocr(filepath: String) {
    // Get the CGImage on which to perform requests.
    guard let cgImage = UIImage(named: filepath)?.cgImage else {
        print("Failed")
        return
    }


    // Create a new image-request handler.
    let requestHandler = VNImageRequestHandler(cgImage: cgImage)


    // Create a new request to recognize text.
    let request = VNRecognizeTextRequest(completionHandler: recognizeTextHandler)


    do {
        // Perform the text-recognition request.
        try requestHandler.perform([request])
    } catch {
        print("(\(filepath)) Unable to perform the requests: \(error).")
    }
}

func recognizeTextHandler(request: VNRequest, error: Error?) {
    guard let observations =
            request.results as? [VNRecognizedTextObservation] else {
        return
    }
    let recognizedStrings = observations.compactMap { observation in
        // Return the string of the top VNRecognizedText instance.
        return observation.topCandidates(1).first?.string
    }
    
    // Process the recognized strings.
    processResults(recognizedStrings)
}

func processResults(_ recognizedStrings: [String]) {
//    print(recognizedStrings)
    let fileUrl = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0].appending(path: "pillarOCR.txt")
    do {
        try recognizedStrings.description.write(to: fileUrl, atomically: true, encoding: .utf8)
    } catch {
        print("Error writing: \(error)")
    }
}

func main() {
    for i in 0...1018 {
        ocr(filepath: "cvs_labels/cvs00003.jpg")
    }
}

main()
