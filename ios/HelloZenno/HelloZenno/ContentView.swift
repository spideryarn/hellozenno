//
//  ContentView.swift
//  HelloZenno
//
//  Created by Greg Detre on 2024-10-28.
//

import SwiftUI
import Foundation


struct ContentView: View {
    @State var greekWord: String = "ανατρέπω"
    
    var body: some View {
        NavigationStack {
            VStack {
                // WordsListView()
                
                SearchboxView(greekWord: $greekWord)
                
                Spacer()
                
                PlayAudioView(word: "temp")

                Spacer()

                RecordAudioView()
                
                Spacer()
                NavigationLink(destination: WordsListView()) {
                    Text("Go to Words List")
                        .padding()
                        .background(Color.blue)
                        .foregroundColor(.white)
                        .cornerRadius(10)
                }
                .padding()
            }
            
            Spacer()
        }
    }
}

#Preview {
    ContentView()
}
