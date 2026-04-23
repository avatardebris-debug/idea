//
//  KeyboardOverlayView.swift
//  RemoteDesktopApp
//
//  Virtual keyboard overlay view
//

import SwiftUI

struct KeyboardOverlayView: View {
    @Binding var isShowing: Bool
    @StateObject private var keyboardOverlay = KeyboardOverlay()
    
    var body: some View {
        ZStack {
            // Keyboard container
            VStack {
                // Special keys row
                HStack {
                    Button(action: { keyboardOverlay.sendBackspace() }) {
                        Label("⌫", systemImage: "delete.left")
                            .font(.title2)
                            .frame(width: 60, height: 50)
                            .background(Color.gray.opacity(0.3))
                            .cornerRadius(5)
                    }
                    
                    Button(action: { keyboardOverlay.sendTab() }) {
                        Label("⇥", systemImage: "tabrate")
                            .font(.title2)
                            .frame(width: 60, height: 50)
                            .background(Color.gray.opacity(0.3))
                            .cornerRadius(5)
                    }
                    
                    Spacer()
                    
                    Button(action: { keyboardOverlay.sendEnter() }) {
                        Label("↵", systemImage: "arrow.down.left")
                            .font(.title2)
                            .frame(width: 80, height: 50)
                            .background(Color.gray.opacity(0.3))
                            .cornerRadius(5)
                    }
                }
                .padding(.horizontal)
                
                Spacer()
                
                // Main keyboard area (placeholder for actual keyboard)
                Text("Virtual Keyboard")
                    .foregroundColor(.white)
                    .padding()
                    .background(Color.gray.opacity(0.3))
                    .cornerRadius(10)
                
                Spacer()
            }
            .frame(maxHeight: .infinity)
            .background(Color.black.opacity(0.8))
            
            // Close button
            Button(action: { isShowing = false }) {
                Image(systemName: "xmark.circle.fill")
                    .font(.title)
                    .foregroundColor(.white)
                    .padding()
                    .background(Color.black.opacity(0.5))
                    .clipShape(Circle())
            }
            .offset(y: -30)
        }
        .transition(.move(edge: .bottom).combined(with: .opacity))
        .animation(.easeInOut(duration: 0.3), value: isShowing)
    }
}

struct KeyboardOverlayView_Previews: PreviewProvider {
    static var previews: some View {
        KeyboardOverlayView(isShowing: .constant(true))
    }
}
