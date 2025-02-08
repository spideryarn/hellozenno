import UIKit

class GreekTextField: UITextField {

    override var textInputMode: UITextInputMode? {
        // Iterate through active input modes (keyboards) to find the Greek keyboard
        for inputMode in UITextInputMode.activeInputModes {
            if let language = inputMode.primaryLanguage, language.hasPrefix("el") {
                // Return the Greek keyboard input mode
                return inputMode
            }
        }
        // If Greek keyboard is not found, use the default input mode
        return super.textInputMode
    }
} 