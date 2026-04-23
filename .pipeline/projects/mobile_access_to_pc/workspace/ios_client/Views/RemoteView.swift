//
//  RemoteView.swift
//  RemoteDesktopApp
//
//  Remote desktop view for displaying PC screen and handling input
//

import SwiftUI

struct RemoteView: View {
    @EnvironmentObject var connectionState: ConnectionState
    @StateObject private var videoDecoder = VideoDecoder()
    @StateObject private var touchHandler = TouchHandler()
    @StateObject private var keyboardOverlay = KeyboardOverlay()
    
    var body: some View {
        ZStack {
            // Video display
            VideoDisplayView(videoDecoder: videoDecoder)
                .edgesIgnoringSafeArea(.all)
            
            // Touch handler (invisible but captures gestures)
            Color.clear
                .gesture(touchHandler.gesture)
                .onTapGesture {
                    touchHandler.handleTap()
                }
                .onLongPressGesture(minimumDuration: 0.5, performs: {
                    touchHandler.handleLongPress()
                })
            
            // Keyboard overlay
            keyboardOverlay.isShowing
                .overlay(KeyboardOverlayView(isShowing: $keyboardOverlay.isShowing))
            
            // Connection status overlay
            if connectionState.status == .error {
                VStack {
                    Text(connectionState.errorMessage)
                        .foregroundColor(.white)
                        .padding()
                        .background(Color.red.opacity(0.8))
                        .cornerRadius(10)
                    Button("Dismiss") {
                        connectionState.reset()
                    }
                    .padding()
                }
            }
            
            // Settings button
            Button(action: showSettings) {
                Image(systemName: "gear")
                    .font(.title2)
                    .foregroundColor(.white)
                    .padding()
                    .background(Color.black.opacity(0.5))
                    .cornerRadius(10)
            }
            .padding()
            .position(x: UIScreen.main.bounds.width - 40, y: 40)
        }
        .onAppear {
            setupKeyboardHandler()
        }
    }
    
    private func setupKeyboardHandler() {
        // Setup keyboard input handling
        NotificationCenter.default.addObserver(
            forName: UIResponder.keyboardDidShowNotification,
            object: nil,
            queue: .main
        ) { _ in
            keyboardOverlay.isShowing = true
        }
        
        NotificationCenter.default.addObserver(
            forName: UIResponder.keyboardWillHideNotification,
            object: nil,
            queue: .main
        ) { _ in
            keyboardOverlay.isShowing = false
        }
    }
    
    private func showSettings() {
        // Future: Add settings view
        print("Settings tapped")
    }
}

struct RemoteView_Previews: PreviewProvider {
    static var previews: some View {
        RemoteView()
    }
}
