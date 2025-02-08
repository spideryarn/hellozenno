//
//  WordView.swift
//  HelloZenno
//
//  Created by Greg Detre on 2024-11-18.
//

import SwiftUI
import Foundation


struct WordData: Codable {
    let canonicalWord: String
    let translation: String
    let etymology: String
    
    enum CodingKeys: String, CodingKey {
        case canonicalWord = "canonical_word"
        case translation
        case etymology
    }
}

struct WordView: View {
    let word: String
    let word_url_base = BASE_URL + "/api/el/words/"
    @State private var wordData: WordData?
    @State private var errorMessage: String?
    
    func fetchWordData() {
        let word_url = word_url_base + word
        guard let url = URL(string: word_url) else {
            print("Invalid URL: \(word_url)")
            errorMessage = "Invalid URL"
            return
        }
        
        print("Starting network request to: \(url)")
        
        URLSession.shared.dataTask(with: url) { data, response, error in
            if let error = error {
                print("Network error: \(error)")
                DispatchQueue.main.async {
                    self.errorMessage = "Network error: \(error.localizedDescription)"
                }
                return
            }
            
            if let httpResponse = response as? HTTPURLResponse {
                print("HTTP Status Code: \(httpResponse.statusCode)")
            }
            
            if let data = data {
                print("Received data of size: \(data.count) bytes")
                
                if let jsonString = String(data: data, encoding: .utf8) {
                    print("Raw JSON: \(jsonString)")
                }
                
                do {
                    let decodedData = try JSONDecoder().decode(WordData.self, from: data)
                    print("Successfully decoded data")
                    DispatchQueue.main.async {
                        self.wordData = decodedData
                        self.errorMessage = nil
                    }
                } catch {
                    print("Decoding error: \(error)")
                    DispatchQueue.main.async {
                        self.errorMessage = "Decoding error: \(error.localizedDescription)"
                    }
                }
            } else {
                print("No data received")
                DispatchQueue.main.async {
                    self.errorMessage = "No data received"
                }
            }
        }.resume()
    }
    
    var body: some View {
        Form {
            Section("Raw Data") {
                if let wordData = wordData {
                    Text("Canonical Word: \(wordData.canonicalWord)")
                    Text("Translation: \(wordData.translation)")
                    Text("Etymology: \(wordData.etymology)")
                } else if let error = errorMessage {
                    Text("Error: \(error)")
                        .foregroundColor(.red)
                } else {
                    Text("Loading...")
                }
            }
        }
        .onAppear {
            fetchWordData()
        }
    }
}

#Preview {
    WordView(word: "ανατρέπω")
}
