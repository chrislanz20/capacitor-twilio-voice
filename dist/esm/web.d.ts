import { WebPlugin } from '@capacitor/core';
import type { CapacitorTwilioVoicePlugin, CallInvite } from './definitions';
export declare class CapacitorTwilioVoiceWeb extends WebPlugin implements CapacitorTwilioVoicePlugin {
    login(_options: {
        accessToken: string;
    }): Promise<{
        success: boolean;
    }>;
    logout(): Promise<{
        success: boolean;
    }>;
    isLoggedIn(): Promise<{
        isLoggedIn: boolean;
        hasValidToken: boolean;
        identity?: string;
    }>;
    makeCall(_options: {
        to: string;
        displayName?: string;
        callerId?: string;
    }): Promise<{
        success: boolean;
        callSid?: string;
    }>;
    acceptCall(_options: {
        callSid: string;
    }): Promise<{
        success: boolean;
    }>;
    rejectCall(_options: {
        callSid: string;
    }): Promise<{
        success: boolean;
    }>;
    endCall(_options: {
        callSid?: string;
    }): Promise<{
        success: boolean;
    }>;
    muteCall(_options: {
        muted: boolean;
        callSid?: string;
    }): Promise<{
        success: boolean;
    }>;
    holdCall(_options: {
        hold: boolean;
        callSid?: string;
    }): Promise<{
        success: boolean;
    }>;
    sendDigits(_options: {
        digits: string;
        callSid?: string;
    }): Promise<{
        success: boolean;
    }>;
    setSpeaker(_options: {
        enabled: boolean;
    }): Promise<{
        success: boolean;
    }>;
    getCallStatus(): Promise<{
        hasActiveCall: boolean;
        isOnHold: boolean;
        isMuted: boolean;
        callSid?: string;
        callState?: string;
        pendingInvites: CallInvite[];
        activeCallsCount: number;
    }>;
    checkMicrophonePermission(): Promise<{
        granted: boolean;
    }>;
    requestMicrophonePermission(): Promise<{
        granted: boolean;
    }>;
    getPluginVersion(): Promise<{
        version: string;
    }>;
}
