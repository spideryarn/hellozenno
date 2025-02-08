//
//  RecordAudioView.swift
//  HelloZenno
//
//  Created by Greg Detre on 2024-11-19.
//

import SwiftUI
import AVFoundation

struct RecordAudioView: View {
    @StateObject private var recorderService = AudioRecorderService.shared
    @StateObject private var playerService = AudioPlayerService.shared
    
    var body: some View {
        HStack(spacing: 40) {
            Button {
                // Normal tap behavior (not used due to pressAction)
            } label: {
                Image(systemName: recorderService.isRecording ? "stop.fill" : "record.circle.fill")
                    .foregroundColor(recorderService.isRecording ? .green : .red)
                    .font(.system(size: 30))
                    .frame(width: 60, height: 60)
                    .background(Circle().fill(.gray).opacity(0.2))
            }
            .pressAction(onPress: {
                playerService.stopAudio()
                recorderService.startRecording()
            }, onRelease: {
                recorderService.stopRecording()
            })
            
            Button {
                if playerService.isPlaying {
                    playerService.pauseAudio()
                } else {
                    recorderService.stopRecording()
                    if let url = recorderService.getLastRecordingURL() {
                        playerService.playAudio(from: url)
                    }
                }
            } label: {
                Image(systemName: playerService.isPlaying ? "pause.circle.fill" : "play.circle.fill")
                    .font(.system(size: 30))
                    .foregroundColor(playerService.isPlaying ? .green : .blue)
                    .frame(width: 60, height: 60)
                    .background(Circle().fill(.gray).opacity(0.2))
            }
            .disabled(!recorderService.hasRecording)
        }
        .onAppear {
            recorderService.setupRecorder()
        }
    }
}

// Custom modifier for handling press and release
struct PressActions: ViewModifier {
    var onPress: () -> Void
    var onRelease: () -> Void
    
    func body(content: Content) -> some View {
        content
            .simultaneousGesture(
                DragGesture(minimumDistance: 0)
                    .onChanged({ _ in
                        onPress()
                    })
                    .onEnded({ _ in
                        onRelease()
                    })
            )
    }
}

extension View {
    func pressAction(onPress: @escaping (() -> Void), onRelease: @escaping (() -> Void)) -> some View {
        modifier(PressActions(onPress: onPress, onRelease: onRelease))
    }
}

struct RecordAudioView_Previews: PreviewProvider {
    static var previews: some View {
        RecordAudioView()
    }
}
