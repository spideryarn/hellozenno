//
//  WordsListView.swift
//  HelloZenno
//
//  Created by Greg Detre on 2024-11-18.
//

import SwiftUI
import Foundation

struct WordsListView: View {
    let words_list_url = BASE_URL + "/api/el/words"
    @State private var words: [String] = []
    @State private var isLoading = true
    
    var body: some View {
        NavigationView {
            if isLoading {
                ProgressView()
            } else {
                List(words, id: \.self) { word in
                    NavigationLink {
                        WordView(word: word)
                    } label: {
                        Text(word)
                            .padding()
                    }
                }
            }
        }
        .onAppear {
            fetchWords()
        }
    }
    
    private func fetchWords() {
        guard let url = URL(string: words_list_url) else { return }
        
        URLSession.shared.dataTask(with: url) { data, response, error in
            if let data = data {
                do {
                    let wordsDict = try JSONDecoder().decode([String: String].self, from: data)
                    DispatchQueue.main.async {
                        self.words = Array(wordsDict.keys).sorted()
                        self.isLoading = false
                    }
                } catch {
                    print("Decoding error: \(error)")
                }
            }
        }.resume()
    }
}

#Preview {
    WordsListView()
}
