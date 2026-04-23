//
//  ContentView.swift
//  RemoteDesktopApp
//
//  Main content view with navigation between connection and remote views
//

import SwiftUI

struct ContentView: View {
    @EnvironmentObject var connectionManager: ConnectionManager
    @StateObject private var connectionState = ConnectionState()
    
    var body: some View {
        TabView {
            ConnectionView(connectionState: connectionState)
                .tabItem {
                    Label("Connect", systemImage: "network")
                }
            
            RemoteView(connectionState: connectionState)
                .tabItem {
                    Label("Remote", systemImage: "ipad")
                }
                .disabled(connectionState.status != .connected)
        }
        .environmentObject(connectionState)
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
