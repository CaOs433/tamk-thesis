//
//  LEDCalibrationView.swift
//  LED-Designer
//
//  Created by Oskari Saarinen on 26.3.2025.
//

import SwiftUI
import AVFoundation
import Vision

struct LEDCalibrationView: View {
    @StateObject private var cameraModel = CameraModel()
    @State private var leds: [(id: Int, position: CGPoint, state: LEDState)] = []
    @State private var currentLEDIndex = 0
    
    enum LEDState {
        case uncalibrated, calibrating, calibrated
    }
    
    var body: some View {
        VStack {
            CameraPreview(session: cameraModel.session)
                .overlay(ledOverlay)
                .onAppear {
                    cameraModel.startSession()
                }
                .onDisappear {
                    cameraModel.stopSession()
                }
            
            Button("Aloita Kalibrointi") {
                startCalibration()
            }
            .padding()
        }
    }
    
    private var ledOverlay: some View {
        ForEach(leds.indices, id: \ .self) { index in
            Circle()
                .fill(leds[index].state == .calibrated ? Color.green : (leds[index].state == .calibrating ? Color.blue : Color.red))
                .frame(width: 10, height: 10)
                .position(leds[index].position)
        }
    }
    
    private func startCalibration() {
        guard !leds.isEmpty else { return }
        calibrateNextLED()
    }
    
    private func calibrateNextLED() {
        guard currentLEDIndex < leds.count else { return }
        
        leds[currentLEDIndex].state = .calibrating
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
            cameraModel.captureImage { detectedPosition in
                if let position = detectedPosition {
                    leds[currentLEDIndex].position = position
                    leds[currentLEDIndex].state = .calibrated
                    currentLEDIndex += 1
                    calibrateNextLED()
                }
            }
        }
    }
}

class CameraModel: NSObject, ObservableObject, AVCapturePhotoCaptureDelegate {
    let session = AVCaptureSession()
    private let output = AVCapturePhotoOutput()
    private let queue = DispatchQueue(label: "camera.queue")
    
    override init() {
        super.init()
        setupCamera()
    }
    
    private func setupCamera() {
        session.beginConfiguration()
        guard let device = AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: .back),
              let input = try? AVCaptureDeviceInput(device: device) else {
            return
        }
        if session.canAddInput(input) { session.addInput(input) }
        if session.canAddOutput(output) { session.addOutput(output) }
        session.commitConfiguration()
    }
    
    func startSession() {
        queue.async {
            self.session.startRunning()
        }
    }
    
    func stopSession() {
        queue.async {
            self.session.stopRunning()
        }
    }
    
    func captureImage(completion: @escaping (CGPoint?) -> Void) {
        let settings = AVCapturePhotoSettings()
        output.capturePhoto(with: settings, delegate: self)
        
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
            self.detectLED(in: UIImage(named: "sample_image")!, completion: completion)
        }
    }
    
    private func detectLED(in image: UIImage, completion: @escaping (CGPoint?) -> Void) {
        guard let cgImage = image.cgImage else {
            completion(nil)
            return
        }
        
        let request = VNDetectRectanglesRequest { request, error in
            guard let results = request.results as? [VNRectangleObservation], error == nil else {
                completion(nil)
                return
            }
            
            if let led = results.first {
                let boundingBox = led.boundingBox
                let x = boundingBox.midX * UIScreen.main.bounds.width
                let y = (1 - boundingBox.midY) * UIScreen.main.bounds.height
                completion(CGPoint(x: x, y: y))
            } else {
                completion(nil)
            }
        }
        
        let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
        try? handler.perform([request])
    }
}

struct CameraPreview: UIViewRepresentable {
    let session: AVCaptureSession
    
    func makeUIView(context: Context) -> UIView {
        let view = UIView()
        let previewLayer = AVCaptureVideoPreviewLayer(session: session)
        previewLayer.videoGravity = .resizeAspectFill
        previewLayer.frame = view.bounds
        view.layer.addSublayer(previewLayer)
        return view
    }
    
    func updateUIView(_ uiView: UIView, context: Context) {}
}

struct LEDCalibrationView_Previews: PreviewProvider {
    static var previews: some View {
        LEDCalibrationView()
    }
}
