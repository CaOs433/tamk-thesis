//
//  LEDStripDesignerView 2.swift
//  LED-Designer
//
//  Created by Oskari Saarinen on 30.1.2025.
//

import SwiftUI

struct LEDStripDesignerView: View {
    @State private var leds: [LED] = []
    @State private var selectedColor: Color = .red
    @State private var isDrawing = false
    @State private var isEditing = false
    @State private var selectedLEDID: UUID?
    @State private var draggingLEDID: UUID?
    
    var body: some View {
        VStack {
            Toggle("Muokkaustila", isOn: $isEditing)
                .padding()
            
            if let selectedLED = leds.first(where: { $0.id == selectedLEDID }) {
                ColorPicker("Muokkaa valittua LEDiä", selection: Binding(
                    get: { selectedLED.color },
                    set: { newValue in
                        if let index = leds.firstIndex(where: { $0.id == selectedLED.id }) {
                            leds[index].color = newValue
                        }
                    }
                ))
                .padding()
            }
            
            Canvas { context, size in
                if leds.count > 1 {
                    let path = Path { path in
                        for i in 0..<leds.count - 1 {
                            path.move(to: leds[i].position)
                            path.addLine(to: leds[i + 1].position)
                        }
                    }
                    context.stroke(path, with: .color(.black), lineWidth: 2)
                }
                
                for (index, led) in leds.enumerated() {
                    let rect = CGRect(x: led.position.x - 5, y: led.position.y - 5, width: 10, height: 10)
                    if index == 0 {
                        context.fill(Path { path in
                            path.move(to: CGPoint(x: led.position.x, y: led.position.y - 5))
                            path.addLine(to: CGPoint(x: led.position.x - 5, y: led.position.y + 5))
                            path.addLine(to: CGPoint(x: led.position.x + 5, y: led.position.y + 5))
                            path.closeSubpath()
                        }, with: .color(led.color))
                    } else if index == leds.count - 1 {
                        context.fill(Path { path in
                            path.addLines([
                                CGPoint(x: led.position.x - 5, y: led.position.y - 3),
                                CGPoint(x: led.position.x - 3, y: led.position.y - 5),
                                CGPoint(x: led.position.x + 3, y: led.position.y - 5),
                                CGPoint(x: led.position.x + 5, y: led.position.y - 3),
                                CGPoint(x: led.position.x + 5, y: led.position.y + 3),
                                CGPoint(x: led.position.x + 3, y: led.position.y + 5),
                                CGPoint(x: led.position.x - 3, y: led.position.y + 5),
                                CGPoint(x: led.position.x - 5, y: led.position.y + 3)
                            ])
                            path.closeSubpath()
                        }, with: .color(led.color))
                    } else {
                        context.fill(Path(ellipseIn: rect), with: .color(led.color))
                    }
                }
            }
            .gesture(DragGesture(minimumDistance: 5)
                .onChanged { value in
                    if isEditing {
                        if draggingLEDID == nil {
                            draggingLEDID = leds.first(where: { abs($0.position.x - value.startLocation.x) < 10 && abs($0.position.y - value.startLocation.y) < 10 })?.id
                        }
                        
                        if let ledID = draggingLEDID, let index = leds.firstIndex(where: { $0.id == ledID }) {
                            let snappedPosition = CGPoint(x: round(value.location.x / 30) * 30, y: round(value.location.y / 30) * 30)
                            if !leds.contains(where: { $0.position == snappedPosition }) {
                                leds[index].position = snappedPosition
                            }
                        }
                    } else {
                        if !isDrawing {
                            isDrawing = true
                        }
                        let snappedPosition = CGPoint(x: round(value.location.x / 30) * 30, y: round(value.location.y / 30) * 30)
                        if !leds.contains(where: { $0.position == snappedPosition }) {
                            leds.append(LED(position: snappedPosition, color: selectedColor))
                        }
                    }
                }
                .onEnded { _ in
                    isDrawing = false
                    draggingLEDID = nil
                }
            )
            .onTapGesture { location in
                if isEditing {
                    selectedLEDID = leds.first(where: { abs($0.position.x - location.x) < 10 && abs($0.position.y - location.y) < 10 })?.id
                }
            }
            .frame(height: 300)
            .border(Color.gray, width: 1)
            .padding()
            
            Button("Tyhjennä") {
                leds.removeAll()
                selectedLEDID = nil
            }
            .padding()
        }
    }
}

#Preview {
    LEDStripDesignerView()
}
