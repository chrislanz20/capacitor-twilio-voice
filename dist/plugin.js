var capacitorCapacitorTwilioVoice = (function (exports, core) {
    'use strict';

    const CapacitorTwilioVoice = core.registerPlugin('CapacitorTwilioVoice', {
        web: () => Promise.resolve().then(function () { return web; }).then((m) => new m.CapacitorTwilioVoiceWeb()),
    });

    class CapacitorTwilioVoiceWeb extends core.WebPlugin {
        // Authentication
        async login(_options) {
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
            throw this.unimplemented('Not implemented on web.');
        }
        async acceptCall(_options) {
            throw this.unimplemented('Not implemented on web.');
        }
        async rejectCall(_options) {
            throw this.unimplemented('Not implemented on web.');
        }
        async endCall(_options) {
            throw this.unimplemented('Not implemented on web.');
        }
        // Call Controls
        async muteCall(_options) {
            throw this.unimplemented('Not implemented on web.');
        }
        async holdCall(_options) {
            throw this.unimplemented('Not implemented on web.');
        }
        async sendDigits(_options) {
            throw this.unimplemented('Not implemented on web.');
        }
        async setSpeaker(_options) {
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

    var web = /*#__PURE__*/Object.freeze({
        __proto__: null,
        CapacitorTwilioVoiceWeb: CapacitorTwilioVoiceWeb
    });

    exports.CapacitorTwilioVoice = CapacitorTwilioVoice;

    return exports;

})({}, capacitorExports);
//# sourceMappingURL=plugin.js.map
