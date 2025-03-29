import AVFoundation

final class AudioRecorderService: BaseAudioService, ObservableObject {
    static let shared = AudioRecorderService()
    
    @Published var isRecording = false
    @Published var hasRecording = false
    
    private var audioRecorder: AVAudioRecorder?
    private var recordedFileURL: URL?
    
    private override init() {
        super.init()
        setupAudioSession()
    }
    
    func setupRecorder() {
        audioRecorder?.stop()
        audioRecorder = nil
        
        let timestamp = Int(Date().timeIntervalSince1970)
        let audioFilename = getDocumentsDirectory().appendingPathComponent("recording_\(timestamp).m4a")
        recordedFileURL = audioFilename
        
        let settings: [String: Any] = [
            AVFormatIDKey: Int(kAudioFormatMPEG4AAC),
            AVSampleRateKey: 44100.0,
            AVNumberOfChannelsKey: 1,
            AVEncoderAudioQualityKey: AVAudioQuality.high.rawValue,
            AVEncoderBitRateKey: 128000,
            AVLinearPCMBitDepthKey: 16
        ]
        
        do {
            audioRecorder = try AVAudioRecorder(url: audioFilename, settings: settings)
            audioRecorder?.delegate = self
            audioRecorder?.prepareToRecord()
        } catch {
            print("Recording setup failed: \(error.localizedDescription)")
        }
    }
    
    func startRecording() {
        setupRecorder()
        audioRecorder?.record()
        isRecording = true
    }
    
    func stopRecording() {
        audioRecorder?.stop()
        isRecording = false
        hasRecording = true
    }
    
    func getLastRecordingURL() -> URL? {
        return recordedFileURL
    }
}

extension AudioRecorderService: AVAudioRecorderDelegate {
    func audioRecorderDidFinishRecording(_ recorder: AVAudioRecorder, successfully flag: Bool) {
        if flag {
            print("Recording finished successfully")
            print("File size: \(try? FileManager.default.attributesOfItem(atPath: recorder.url.path)[.size] ?? 0)")
        } else {
            print("Recording finished with error")
        }
    }
} 