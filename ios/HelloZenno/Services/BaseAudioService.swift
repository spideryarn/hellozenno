import AVFoundation

class BaseAudioService: NSObject {
    func setupAudioSession() {
        do {
            let session = AVAudioSession.sharedInstance()
            try session.setCategory(.playAndRecord, 
                options: [.defaultToSpeaker, .allowBluetooth, .mixWithOthers])
            try session.setMode(.default)
            try session.setActive(true, options: .notifyOthersOnDeactivation)
        } catch {
            print("Failed to set up audio session: \(error.localizedDescription)")
        }
    }
    
    func getDocumentsDirectory() -> URL {
        FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
    }
} 