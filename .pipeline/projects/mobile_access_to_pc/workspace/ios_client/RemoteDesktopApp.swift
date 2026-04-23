//
//  RemoteDesktopApp.swift
//  RemoteDesktopApp
//
//  Main app entry point for Mobile Access to PC iOS client
//

import SwiftUI

@main
struct RemoteDesktopApp: App {
    @StateObject private var connectionManager = ConnectionManager()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(connectionManager)
        }
    }
}
