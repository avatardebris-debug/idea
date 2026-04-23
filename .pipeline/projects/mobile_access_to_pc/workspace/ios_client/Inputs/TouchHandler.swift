//
//  TouchHandler.swift
//  RemoteDesktopApp
//
//  Handles touch input and converts it to mouse movements
//

import Foundation
import UIKit

class TouchHandler: NSObject, ObservableObject {
    @Published var isDragging = false
    @Published var lastTapLocation: CGPoint?
    
    private var connectionManager: ConnectionManager?
    
    override init() {
        super.init()
    }
    
    func setup(connectionManager: ConnectionManager) {
        self.connectionManager = connectionManager
    }
    
    func handleTap() {
        guard let manager = connectionManager else { return }
        
        // Send mouse click
        manager.send(mouseClick: "left")
    }
    
    func handleLongPress() {
        guard let manager = connectionManager else { return }
        
        // Send right-click for long press
        manager.send(mouseClick: "right")
    }
    
    func handleDrag(from start: CGPoint, to end: CGPoint) {
        guard let manager = connectionManager else { return }
        
        // Send mouse move to start position
        manager.send(mouseMove: Int(start.x), y: Int(start.y))
        manager.send(mouseClick: "left")
        
        // Send mouse move to end position
        manager.send(mouseMove: Int(end.x), y: Int(end.y))
    }
    
    func handleScroll(deltaY: Int) {
        guard let manager = connectionManager else { return }
        
        // Get current position or use center
        let position = lastTapLocation ?? CGPoint(x: UIScreen.main.bounds.width / 2, y: UIScreen.main.bounds.height / 2)
        
        manager.send(scroll: Int(position.x), y: Int(position.y), deltaY: deltaY)
    }
    
    func updateLastTapLocation(_ location: CGPoint) {
        self.lastTapLocation = location
    }
}

// MARK: - Gesture Recognizer
class CustomGestureRecognizer: UIGestureRecognizer {
    override func touchesEnded(_ touches: Set<UITouch>, with event: UIEvent) {
        guard let touch = touches.first else { return }
        
        if location(in: view).x < 100 && location(in: view).y < 100 {
            // Corner tap - special handling
            state = .cancelled
        } else {
            state = .ended
        }
    }
}
