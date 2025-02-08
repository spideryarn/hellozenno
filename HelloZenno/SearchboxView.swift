//
//  SearchboxView.swift
//  HelloZenno
//
//  Created by Greg Detre on 2024-11-19.
//

import SwiftUI

struct SearchboxView: View {
    @Binding var greekWord: String
    
    var body: some View {
        Section("Greek word") {
            HStack {
                Image(systemName: "magnifyingglass")
                    .foregroundColor(.gray)
                GreekTextFieldWrapper(text: $greekWord)
            }
            .padding(.horizontal)
            .frame(height: 40)
            .background(Color(.systemBackground))
            .overlay(
                RoundedRectangle(cornerRadius: 10)
                    .stroke(Color.gray, lineWidth: 1)
            )
            .padding(.horizontal)
        }
    }
}

struct SearchboxView_Previews: PreviewProvider {
    static var previews: some View {
        SearchboxView(greekWord: .constant(""))
    }
}

