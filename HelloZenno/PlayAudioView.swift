//
//  AudioView.swift
//  HelloZenno
//
//  Created by Greg Detre on 2024-11-19.
//

import Foundation
import SwiftUI
import AVFoundation


struct PlayAudioView: View {
    let word: String
    let mp3_url: String
    
    init(word: String) {
        self.word = word
        self.mp3_url = BASE_URL + "/api/el/words/\(word)/mp3"
    }
    
    // Add function to get documents directory path
    private func getLocalFilePath() -> URL {
        let documentsPath = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        return documentsPath.appendingPathComponent("\(word).mp3")
    }
    
    // Add function to ensure audio file exists
    private func ensureAudioFileExists() async throws {
        let localURL = getLocalFilePath()
        
        // Check if file already exists
        if FileManager.default.fileExists(atPath: localURL.path) {
            print("Audio file already exists for word: \(word)")
            return
        }
        
        // Download and save file
        guard let url = URL(string: mp3_url) else {
            throw URLError(.badURL)
        }
        
        let (downloadedFileURL, _) = try await URLSession.shared.download(from: url)
        try FileManager.default.moveItem(at: downloadedFileURL, to: localURL)
        print("Downloaded and saved audio file for word: \(word)")
    }
    
    @StateObject private var playerService = AudioPlayerService.shared
    
    var body: some View {
        VStack(spacing: 8) {
            HStack(spacing: 30) {
                Button {
                    Task {
                        do {
                            try await ensureAudioFileExists()
                            let localURL = getLocalFilePath()
                            playerService.rewindAndPlay(seconds: 2)
                        } catch {
                            print("Error preparing audio: \(error)")
                        }
                    }
                } label: {
                    Image(systemName: "gobackward")
                        .foregroundColor(.blue)
                        .font(.system(size: 30))
                        .frame(width: 60, height: 60)
                        .background(Circle().fill(.gray).opacity(0.2))
                }
                
                Button {
                    if playerService.isPlaying {
                        playerService.pauseAudio()
                    } else {
                        // Wrap in Task since we're calling async function
                        Task {
                            do {
                                try await ensureAudioFileExists()
                                let localURL = getLocalFilePath()
                                playerService.playAudio(from: localURL)
                            } catch {
                                print("Error preparing audio: \(error)")
                            }
                        }
                    }
                } label: {
                    Image(systemName: playerService.isPlaying ? "pause.circle.fill" : "play.circle.fill")
                        .foregroundColor(playerService.isPlaying ? .green : .blue)
                        .font(.system(size: 30))
                        .frame(width: 60, height: 60)
                        .background(Circle().fill(.gray).opacity(0.2))
                }
                
                Button {
                    playerService.skipForward(seconds: 15)
                } label: {
                    Image(systemName: "goforward")
                        .foregroundColor(.blue)
                        .font(.system(size: 30))
                        .frame(width: 60, height: 60)
                        .background(Circle().fill(.gray).opacity(0.2))
                }
                
                Button {
                    playerService.stopAudio()
                } label: {
                    Image(systemName: "backward.end.circle.fill")
                        .foregroundColor(.blue)
                        .font(.system(size: 30))
                        .frame(width: 60, height: 60)
                        .background(Circle().fill(.gray).opacity(0.2))
                }
            }
            
            // Progress bar
            GeometryReader { geometry in
                ZStack(alignment: .leading) {
                    Rectangle()
                        .fill(.gray.opacity(0.2))
                        .frame(height: 2)
                    
                    Rectangle()
                        .fill(.blue)
                        .frame(width: geometry.size.width * playerService.progress, height: 2)
                }
            }
            // keep this line as a reminder in case we want to go back to a more general way of doing things
            // .frame(height: 2)  // Constrain the height of GeometryReader
            .frame(width: (60 * 4) + (30 * 3), height: 2)  // 4 buttons * 60 width + 3 spaces * 30
        }
        .frame(width: 300)
    }
}

struct AudioView_Previews: PreviewProvider {
    static var previews: some View {
        PlayAudioView(word: "example")
    }
}
