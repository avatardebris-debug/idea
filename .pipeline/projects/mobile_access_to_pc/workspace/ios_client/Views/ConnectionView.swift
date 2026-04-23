//
//  ConnectionView.swift
//  RemoteDesktopApp
//
//  Connection screen for entering server details
//

import SwiftUI

struct ConnectionView: View {
    @EnvironmentObject var connectionState: ConnectionState
    @State private var ipAddress: String = ""
    @State private var port: String = "8765"
    
    var body: some View {
        NavigationView {
            Group {
                if connectionState.status == .connected {
                    ConnectedView(connectionState: connectionState)
                } else {
                    DisconnectedView(
                        ipAddress: $ipAddress,
                        port: $port,
                        connectionState: connectionState
                    )
                }
            }
            .navigationTitle("Connect to PC")
        }
    }
}

struct DisconnectedView: View {
    @Binding var ipAddress: String
    @Binding var port: String
    @EnvironmentObject var connectionState: ConnectionState
    
    var body: some View {
        Form {
            Section(header: Text("Server Settings")) {
                TextField("PC IP Address", text: $ipAddress)
                    .keyboardType(.numberPad)
                    .autocapitalization(.none)
                
                TextField("Port", text: $port)
                    .keyboardType(.numberPad)
                    .autocapitalization(.none)
                    .textContentType(.URL)
            }
            
            Section(header: Text("Connection Status")) {
                HStack {
                    Text("Status:")
                    Spacer()
                    Text(connectionState.status.rawValue)
                        .fontWeight(.bold)
                        .foregroundColor(statusColor)
                }
                
                if !connectionState.errorMessage.isEmpty {
                    Text(connectionState.errorMessage)
                        .foregroundColor(.red)
                        .font(.caption)
                }
            }
            
            Section(header: Text("Instructions")) {
                VStack(alignment: .leading, spacing: 8) {
                    Text("1. Make sure the PC agent is running")
                    Text("2. Enter the PC's IP address")
                    Text("3. Tap 'Connect' to establish connection")
                    Text("4. Both devices should be on the same network")
                }
                .font(.caption)
                .foregroundColor(.secondary)
            }
        }
        .toolbar {
            ToolbarItem(placement: .primaryAction) {
                Button("Connect") {
                    connect()
                }
                .disabled(ipAddress.isEmpty || port.isEmpty)
                .fontWeight(.bold)
            }
        }
    }
    
    private var statusColor: Color {
        switch connectionState.status {
        case .connected:
            return .green
        case .connecting:
            return .blue
        case .error:
            return .red
        case .disconnected:
            return .gray
        }
    }
    
    private func connect() {
        if let portInt = Int(port), portInt > 0 && portInt < 65535 {
            connectionState.connect(toIP: ipAddress, port: portInt)
        } else {
            connectionState.onError(message: "Invalid port number")
        }
    }
}

struct ConnectedView: View {
    @EnvironmentObject var connectionState: ConnectionState
    
    var body: some View {
        Form {
            Section(header: Text("Connected")) {
                HStack {
                    Text("PC IP:")
                    Spacer()
                    Text(connectionState.serverIP)
                        .fontWeight(.bold)
                }
                
                HStack {
                    Text("Port:")
                    Spacer()
                    Text("\(connectionState.serverPort)")
                        .fontWeight(.bold)
                }
                
                HStack {
                    Text("Resolution:")
                    Spacer()
                    Text("\(connectionState.screenWidth)x\(connectionState.screenHeight)")
                        .fontWeight(.bold)
                }
            }
            
            Section {
                Button(action: disconnect) {
                    HStack {
                        Image(systemName: "power")
                        Text("Disconnect")
                    }
                    .foregroundColor(.red)
                }
            }
        }
    }
    
    private func disconnect() {
        connectionState.reset()
    }
}

struct ConnectionView_Previews: PreviewProvider {
    static var previews: some View {
        NavigationView {
            ConnectionView()
        }
    }
}
