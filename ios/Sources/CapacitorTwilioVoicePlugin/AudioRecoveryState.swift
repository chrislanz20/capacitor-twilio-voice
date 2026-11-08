import Foundation

// Structured error data only. No recovery policy lives here.
struct AudioRecoveryFailure {
    let phase: String
    let error: NSError

    var diagnostic: [String: Any] {
        ["action": "activation-failed", "phase": phase,
         "error": "Audio session activation failed",
         "errorDomain": String(error.domain.prefix(96)), "errorCode": error.code,
         // Apple's own text for the refusal. Carries no user data.
         "errorMessage": String(error.localizedDescription.prefix(160))]
    }
}
