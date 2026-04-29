import { WebPlugin } from '@capacitor/core';
export class CapacitorTwilioVoiceWeb extends WebPlugin {
    // Authentication
    async login(_options) {
        void _options;
        throw this.unimplemented('Not implemented on web.');
    }
    async logout() {
        throw this.unimplemented('Not implemented on web.');
    }
    async isLoggedIn() {
        throw this.unimplemented('Not implemented on web.');
    }
    // Call Management
    async makeCall(_options) {
        void _options;
        throw this.unimplemented('Not implemented on web.');
    }
    async acceptCall(_options) {
        void _options;
        throw this.unimplemented('Not implemented on web.');
    }
    async rejectCall(_options) {
        void _options;
        throw this.unimplemented('Not implemented on web.');
    }
    async endCall(_options) {
        void _options;
        throw this.unimplemented('Not implemented on web.');
    }
    // Call Controls
    async muteCall(_options) {
        void _options;
        throw this.unimplemented('Not implemented on web.');
    }
    async holdCall(_options) {
        void _options;
        throw this.unimplemented('Not implemented on web.');
    }
    async sendDigits(_options) {
        void _options;
        throw this.unimplemented('Not implemented on web.');
    }
    async setSpeaker(_options) {
        void _options;
        throw this.unimplemented('Not implemented on web.');
    }
    // Call Status
    async getCallStatus() {
        throw this.unimplemented('Not implemented on web.');
    }
    // Audio Permissions
    async checkMicrophonePermission() {
        throw this.unimplemented('Not implemented on web.');
    }
    async requestMicrophonePermission() {
        throw this.unimplemented('Not implemented on web.');
    }
    async getPluginVersion() {
        return { version: 'web' };
    }
}
//# sourceMappingURL=web.js.map