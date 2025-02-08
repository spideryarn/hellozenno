import AVFoundation

final class AudioPlayerService: BaseAudioService, ObservableObject {
    static let shared = AudioPlayerService()
    
    @Published var isPlaying = false
    
    private var audioPlayer: AVAudioPlayer?
    
    private var progressTimer: Timer?
    @Published private(set) var progress: Double = 0
    
    private override init() {
        super.init()
        setupAudioSession()
    }
    
    func playAudio(from url: URL) {
        do {
            print("Attempting to play audio from: \(url.path)")
            
            // Check if file exists
            guard FileManager.default.fileExists(atPath: url.path) else {
                print("File does not exist at path: \(url.path)")
                return
            }
            
            audioPlayer = try AVAudioPlayer(contentsOf: url)
            guard let player = audioPlayer else {
                print("Failed to create audio player")
                return
            }
            
            player.delegate = self
            
            if player.prepareToPlay() {
                player.play()
                isPlaying = true
                startProgressTracking()
                print("Audio playback started successfully")
                print("Duration: \(player.duration) seconds")
            } else {
                print("Failed to prepare audio player")
            }
        } catch {
            print("Playback failed with error: \(error)")
            print("Detailed error: \(error.localizedDescription)")
        }
    }
    
    private func startProgressTracking() {
        // Invalidate existing timer if any
        progressTimer?.invalidate()
        
        // Create new timer that updates progress every 0.1 seconds
        progressTimer = Timer.scheduledTimer(withTimeInterval: 0.1, repeats: true) { [weak self] _ in
            guard let self = self,
                  let player = self.audioPlayer else { return }
            
            self.progress = player.currentTime / player.duration
        }
    }
    
    func pauseAudio() {
        audioPlayer?.pause()
        isPlaying = false
        progressTimer?.invalidate()
    }
    
    func stopAudio() {
        audioPlayer?.stop()
        audioPlayer?.currentTime = 0
        isPlaying = false
        progressTimer?.invalidate()
        progress = 0
    }
    
    func rewindAndPlay(seconds: Double) {
        guard let player = audioPlayer else {
            // If no player exists, do nothing
            return
        }
        
        // Calculate new time
        let newTime = max(0, player.currentTime - seconds)
        player.currentTime = newTime
        
        // Start playing
        player.play()
        isPlaying = true
    }
    
    func skipForward(seconds: Double) {
        guard let player = audioPlayer else {
            // If no player exists, do nothing
            return
        }
        
        // Calculate new time
        let newTime = min(player.duration, player.currentTime + seconds)
        player.currentTime = newTime
        
        // Ensure playing continues
        if isPlaying {
            player.play()
        }
    }
}

extension AudioPlayerService: AVAudioPlayerDelegate {
    func audioPlayerDidFinishPlaying(_ player: AVAudioPlayer, successfully flag: Bool) {
        isPlaying = false
    }
} 