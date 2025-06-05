//
//  LEDStripDesignerView.swift
//  LED-Designer
//
//  Created by Oskari Saarinen on 29.1.2025.
//

import SwiftUI

struct LEDDrawingView: View {
    @State private var path = Path()
    @State private var drawing = false
    @State private var leds: [LED] = []
    
    var body: some View {
        VStack {
            ZStack {
                Color.white
                    .gesture(DragGesture(minimumDistance: 0, coordinateSpace: .local)
                        .onChanged { value in
                            if !drawing {
                                drawing = true
                                path.move(to: value.location)
                            }
                            path.addLine(to: value.location)
                        }
                        .onEnded { value in
                            drawing = false
                            renderLEDs(from: path)
                        })
                
                ForEach(leds.indices, id: \.self) { index in
                    let led = leds[index]
                    Circle()
                        .frame(width: led.size, height: led.size)
                        .position(led.position)
                        .foregroundColor(led.color)
                        .overlay(
                            ColorPicker("Väri", selection: $leds[index].color)
                                .frame(width: 120)
                                .offset(x: 0, y: 25)
                        )
                }
            }
            .frame(height: 400)
            .border(Color.black, width: 1)
            
            Spacer()
        }
    }
    
    private func renderLEDs(from path: Path) {
        var newLEDs: [LED] = []
        
        let points = extractPoints(from: path)
        
        var currentLength: CGFloat = 0
        let stepSize: CGFloat = 10.0
        var index = 0
        
        for i in 1..<points.count {
            let start = points[i - 1]
            let end = points[i]
            let segmentLength = distance(from: start, to: end)
            
            currentLength += segmentLength
            
            while currentLength >= stepSize {
                // Pisteen luominen segmentin pituuden perusteella
                let ratio = (currentLength - stepSize) / segmentLength
                let position = CGPoint(x: start.x + (end.x - start.x) * ratio,
                                       y: start.y + (end.y - start.y) * ratio)
                
                let size = (index % 2 == 0) ? 10 : 20
                newLEDs.append(LED(id: UUID(), position: position, size: CGFloat(size), color: .blue))
                
                currentLength -= stepSize
                index += 1
            }
        }
        
        leds = newLEDs
    }
    
    private func extractPoints(from path: Path) -> [CGPoint] {
        var points: [CGPoint] = []
        path.forEach { element in
            switch element {
            case .move(to: let point):
                points.append(point)
            case .line(to: let point):
                points.append(point)
            default:
                break
            }
        }
        return points
    }
    
    private func distance(from start: CGPoint, to end: CGPoint) -> CGFloat {
        let dx = end.x - start.x
        let dy = end.y - start.y
        return sqrt(dx * dx + dy * dy) / 2
    }
}

struct LED: Identifiable {
    var id: UUID = UUID()
    var position: CGPoint = .zero
    var size: CGFloat = 10
    var color: Color
}

#Preview {
    LEDDrawingView()
}
