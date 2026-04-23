//
//  VideoDisplayView.swift
//  RemoteDesktopApp
//
//  Video display component for showing PC screen
//

import SwiftUI
import AVFoundation

struct VideoDisplayView: UIViewRepresentable {
    @ObservedObject var videoDecoder: VideoDecoder
    
    func makeUIView(context: Context) -> UIView {
        let view = UIView()
        
        // Create image view for displaying frames
        let imageView = UIImageView(frame: view.bounds)
        imageView.contentMode = .scaleAspectFit
        imageView.backgroundColor = .black
        imageView.clipsToBounds = true
        
        view.addSubview(imageView)
        
        // Setup observer for video updates
        NotificationCenter.default.addObserver(
            forName: .videoFrameUpdated,
            object: nil,
            queue: .main
        ) { [weak imageView] _ in
            Task { @MainActor in
                if let image = videoDecoder.currentFrame {
                    imageView?.image = image
                }
            }
        }
        
        return view
    }
    
    func updateUIView(_ uiView: UIView, context: Context) {
        // Update frame size if changed
        uiView.frame = UIScreen.main.bounds
    }
    
    static func makeCoordinator() -> Coordinator {
        Coordinator()
    }
    
    class Coordinator: NSObject {
        var parent: VideoDisplayView
        
        init() {
            self.parent = VideoDisplayView(videoDecoder: VideoDecoder())
        }
    }
}

// MARK: - Extensions
extension Notification.Name {
    static let videoFrameUpdated = Notification.Name("videoFrameUpdated")
}

// MARK: - Preview
struct VideoDisplayView_Previews: PreviewProvider {
    static var previews: some View {
        VideoDisplayView(videoDecoder: VideoDecoder())
            .frame(minWidth: 300, minHeight: 400)
    }
}
