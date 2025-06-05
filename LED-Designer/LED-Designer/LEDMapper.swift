//
//  LEDMapper.swift
//  LED-Designer
//
//  Created by Oskari Saarinen on 26.3.2025.
//

import SwiftUI

class LEDMapper {
    let ledController: LEDController
    var leds: [LEDMapper.LED]
    
    init () {
        // Initialize the LEDMapper
        self.leds = []
        self.ledController = LEDController()
    }
    
    struct LED: Identifiable {
        var id: UUID = UUID()
        var address: String
        var color: Color
        var brightness: Double
        
    }
}

class LEDController {
    
    init () {
        
    }
    
    
}
