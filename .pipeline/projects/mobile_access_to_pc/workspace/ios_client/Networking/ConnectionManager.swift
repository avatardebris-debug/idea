//
//  ConnectionManager.swift
//  RemoteDesktopApp
//
//  Manages WebSocket connection lifecycle
//

import Foundation

class ConnectionManager: ObservableObject {
    @Published var connectionState: ConnectionState = ConnectionState()
    @Published var wsClient: WebSocketClient?
    
    private var connectionTask: Task<Void, Never>?
    
    init() {
        setupObservers()
    }
    
    private func setupObservers() {
        NotificationCenter.default.addObserver(
            forName: .screenDimensionsChanged,
            object: nil,
            queue: .main
        ) { [weak self] notification in
            guard let userInfo = notification.userInfo,
                  let width = userInfo["width"] as? Int,
                  let height = userInfo["height"] as? Int else { return }
            
            self?.connectionState.onConnected(width: width, height: height)
        }
    }
    
    func connect(toIP: String, port: Int) {
        connectionState.connect(toIP: toIP, port: port)
        
        // Create new WebSocket client
        wsClient = WebSocketClient(serverIP: toIP, serverPort: port)
        
        // Start connection task
        connectionTask?.cancel()
        connectionTask = Task {
            await connectTask()
        }
    }
    
    func disconnect() {
        wsClient?.disconnect()
        wsClient = nil
        connectionState.reset()
        connectionTask?.cancel()
    }
    
    private func connectTask() async {
        guard let client = wsClient else { return }
        
        while !Task.isCancelled {
            await MainActor.run {
                client.connect()
            }
            
            // Wait for connection or cancellation
            try? await Task.sleep(nanoseconds: 1_000_000_000) // 1 second
            
            if client.isConnected {
                break
            }
            
            // Check for error state
            await MainActor.run {
                if connectionState.status == .error {
                    break
                }
            }
        }
    }
    
    func send(mouseMove x: Int, y: Int) {
        guard let client = wsClient else { return }
        
        let data: [String: Any] = [
            "type": "mouse_move",
            "x": x,
            "y": y
        ]
        
        if let json = try? JSONSerialization.data(withJSONObject: data),
           let text = String(data: json, encoding: .utf8) {
            client.send(text: text)
        }
    }
    
    func send(mouseClick button: String) {
        guard let client = wsClient else { return }
        
        let data: [String: Any] = [
            "type": "mouse_click",
            "button": button
        ]
        
        if let json = try? JSONSerialization.data(withJSONObject: data),
           let text = String(data: json, encoding: .utf8) {
            client.send(text: text)
        }
    }
    
    func send(keyPress key: String, modifiers: [String] = []) {
        guard let client = wsClient else { return }
        
        var data: [String: Any] = [
            "type": "key_press",
            "key": key
        ]
        
        if !modifiers.isEmpty {
            data["modifiers"] = modifiers
        }
        
        if let json = try? JSONSerialization.data(withJSONObject: data),
           let text = String(data: json, encoding: .utf8) {
            client.send(text: text)
        }
    }
    
    func send(text: String) {
        guard let client = wsClient else { return }
        
        let data: [String: Any] = [
            "type": "keyboard_text",
            "text": text
        ]
        
        if let json = try? JSONSerialization.data(withJSONObject: data),
           let text = String(data: json, encoding: .utf8) {
            client.send(text: text)
        }
    }
    
    func send(touch x: Int, y: Int, screenWidth: Int, screenHeight: Int) {
        guard let client = wsClient else { return }
        
        let data: [String: Any] = [
            "type": "touch",
            "x": x,
            "y": y,
            "screen_width": screenWidth,
            "screen_height": screenHeight
        ]
        
        if let json = try? JSONSerialization.data(withJSONObject: data),
           let text = String(data: json, encoding: .utf8) {
            client.send(text: text)
        }
    }
}
