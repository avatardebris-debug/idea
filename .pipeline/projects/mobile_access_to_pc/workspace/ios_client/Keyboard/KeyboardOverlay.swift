//
//  KeyboardOverlay.swift
//  RemoteDesktopApp
//
//  Manages keyboard overlay state
//

import Foundation

class KeyboardOverlay: ObservableObject {
    @Published var isShowing = false
    @Published var currentText: String = ""
    
    private var connectionManager: ConnectionManager?
    
    func setup(connectionManager: ConnectionManager) {
        self.connectionManager = connectionManager
    }
    
    func sendText(_ text: String) {
        guard let manager = connectionManager else { return }
        
        // Send text character by character
        for char in text {
            if char == " " {
                manager.send(keyPress: "space")
            } else if char == "\n" {
                manager.send(keyPress: "return")
            } else if char == "\t" {
                manager.send(keyPress: "tab")
            } else if let ascii = char.asciiValue {
                // Regular character
                manager.send(keyPress: String(char))
            }
            
            // Small delay between characters
            try? Task.sleep(nanoseconds: 50_000_000) // 50ms
        }
    }
    
    func sendBackspace() {
        guard let manager = connectionManager else { return }
        manager.send(keyPress: "delete")
    }
    
    func sendEnter() {
        guard let manager = connectionManager else { return }
        manager.send(keyPress: "return")
    }
    
    func sendTab() {
        guard let manager = connectionManager else { return }
        manager.send(keyPress: "tab")
    }
    
    func clear() {
        self.currentText = ""
    }
}
