//
//  WebSocketClient.swift
//  RemoteDesktopApp
//
//  WebSocket client for bidirectional communication with PC agent
//

import Foundation
import Starscream

class WebSocketClient: NSObject, ObservableObject {
    @Published var isConnected = false
    @Published var lastError: String?
    
    private var websocket: WebSocket?
    private var reconnectTimer: Timer?
    private var reconnectDelay: Double = 1.0
    
    private let serverIP: String
    private let serverPort: Int
    
    init(serverIP: String, serverPort: Int) {
        self.serverIP = serverIP
        self.serverPort = serverPort
        super.init()
    }
    
    func connect() {
        let url = URL(string: "ws://\(serverIP):\(serverPort)")!
        websocket = WebSocket(url: url)
        websocket?.delegate = self
        websocket?.connect()
        
        reconnectDelay = 1.0 // Reset delay on new connection attempt
    }
    
    func disconnect() {
        websocket?.disconnect()
        websocket = nil
        isConnected = false
        stopReconnectTimer()
    }
    
    func send(data: Data) {
        guard let websocket = websocket, websocket.isConnected else {
            lastError = "Not connected"
            return
        }
        websocket.write(data: data)
    }
    
    func send(text: String) {
        guard let websocket = websocket, websocket.isConnected else {
            lastError = "Not connected"
            return
        }
        websocket.write(text: text)
    }
    
    private func startReconnectTimer() {
        stopReconnectTimer()
        reconnectTimer = Timer.scheduledTimer(withTimeInterval: reconnectDelay, repeats: false) { [weak self] _ in
            self?.connect()
            self?.reconnectDelay = min(self?.reconnectDelay * 2 ?? 1.0, 30.0) // Exponential backoff, max 30s
        }
    }
    
    private func stopReconnectTimer() {
        reconnectTimer?.invalidate()
        reconnectTimer = nil
    }
}

extension WebSocketClient: WebSocketDelegate {
    func websocketDidConnect(socket: WebSocketClient) {
        print("WebSocket connected")
        isConnected = true
        reconnectDelay = 1.0
    }
    
    func websocketDidDisconnect(socket: WebSocketClient, error: Error?) {
        print("WebSocket disconnected: \(error?.localizedDescription ?? "unknown")")
        isConnected = false
        startReconnectTimer()
    }
    
    func websocketDidReceiveData(socket: WebSocketClient, data: Data) {
        // Handle binary data (video frames)
        Task {
            await MainActor.run {
                // This would trigger video frame update
            }
        }
    }
    
    func websocketDidReceiveMessage(socket: WebSocketClient, text: String) {
        // Handle text messages (JSON)
        if let jsonData = text.data(using: .utf8) {
            if let message = try? JSONSerialization.jsonObject(with: jsonData) as? [String: Any] {
                handleMessage(message)
            }
        }
    }
    
    private func handleMessage(_ message: [String: Any]) {
        guard let type = message["type"] as? String else { return }
        
        switch type {
        case "connected":
            if let width = message["screen_width"] as? Int,
               let height = message["screen_height"] as? Int {
                NotificationCenter.default.post(
                    name: .screenDimensionsChanged,
                    object: nil,
                    userInfo: ["width": width, "height": height]
                )
            }
            
        case "heartbeat_ack":
            // Heartbeat acknowledged
            
        case "error":
            if let error = message["message"] as? String {
                lastError = error
            }
            
        default:
            print("Unknown message type: \(type)")
        }
    }
}

extension Notification.Name {
    static let screenDimensionsChanged = Notification.Name("screenDimensionsChanged")
}
