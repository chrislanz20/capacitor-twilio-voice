import Foundation

// Pure state policy. No CallKit identity or AVAudioSession operation lives here.
struct AudioRecoveryState {
    let generation: Int
    let tokenMatches: Bool
    let connected: Bool
    let held: Bool
    let muted: Bool
    let otherCallKitCalls: Int
    let otherPluginCalls: Int

    var permitsRecovery: Bool {
        tokenMatches && connected && !held && !muted
            && otherCallKitCalls == 0 && otherPluginCalls == 0
    }

    func permitsDelayedRecovery(after capturedGeneration: Int) -> Bool {
        generation == capturedGeneration && permitsRecovery
    }
}

struct AudioRecoveryFailure {
    let phase: String
    let error: NSError

    var diagnostic: [String: Any] {
        ["action": "activation-failed", "phase": phase,
         "error": "Audio session activation failed",
         "errorDomain": String(error.domain.prefix(96)), "errorCode": error.code]
    }
}
