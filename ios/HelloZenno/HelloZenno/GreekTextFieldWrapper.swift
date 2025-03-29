import SwiftUI
import UIKit

struct GreekTextFieldWrapper: UIViewRepresentable {
    typealias UIViewType = GreekTextField
    
    @Binding var text: String

    func makeUIView(context: Context) -> GreekTextField {
        let textField = GreekTextField()
        textField.delegate = context.coordinator
        textField.font = UIFont.systemFont(ofSize: 24)
        textField.autocorrectionType = .no
        textField.autocapitalizationType = .none
        return textField
    }

    func updateUIView(_ uiView: GreekTextField, context: Context) {
        uiView.text = text
    }

    func makeCoordinator() -> Coordinator {
        Coordinator(text: $text)
    }

    class Coordinator: NSObject, UITextFieldDelegate {
        @Binding var text: String

        init(text: Binding<String>) {
            _text = text
        }

        func textFieldDidChangeSelection(_ textField: UITextField) {
            text = textField.text ?? ""
        }
    }
} 
