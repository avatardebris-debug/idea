//
//  ConnectionState.swift
//  RemoteDesktopApp
//
//  Manages connection state for the remote desktop app
//

import Foundation
import Combine

enum ConnectionStatus: String, Equatable {
    case disconnected
    case connecting
    case connected
    case error
}

class ConnectionState: ObservableObject {
    @Published var status: ConnectionStatus = .disconnected
    @Published var errorMessage: String = ""
    @Published var serverIP: String = ""
    @Published var serverPort: Int = 8765
    @Published var screenWidth: Int = 0
    @Published var screenHeight: Int = 0
    
    private var reconnectTimer: Timer?
    
    func connect(toIP: String, port: Int) {
        self.serverIP = toIP
        self.serverPort = port
        self.status = .connecting
        self.errorMessage = ""
    }
    
    func onConnected(width: Int, height: Int) {
        self.screenWidth = width
        self.screenHeight = height
        self.status = .connected
        self.stopReconnectTimer()
    }
    
    func onDisconnected() {
        self.status = .disconnected
        self.startReconnectTimer()
    }
    
    func onError(message: String) {
        self.status = .error
        self.errorMessage = message
        self.startReconnectTimer()
    }
    
    private func startReconnectTimer() {
        self.stopReconnectTimer()
        self.reconnectTimer = Timer.scheduledTimer(withTimeInterval: 3.0, repeats: false) { [weak self] _ in
            self?.status = .disconnected
            self?.errorMessage = ""
        }
    }
    
    func stopReconnectTimer() {
        self.reconnectTimer?.invalidate()
        self.reconnectTimer = nil
    }
    
    func reset() {
        self.status = .disconnected
        self.errorMessage = ""
        self.screenWidth = 0
        self.screenHeight = 0
        self.stopReconnectTimer()
    }
}
