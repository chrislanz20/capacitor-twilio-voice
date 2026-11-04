"""Run actual Swift recovery method/policy with Foundation-only invented boundaries.
No iOS, CallKit, audio hardware, providers, credentials or network are used.
AUDIO_RECOVERY_SOURCE optionally selects an old source for baseline RED.
AUDIO_RECOVERY_FAULT mutates source only in memory. No repository restore needed.
"""
from pathlib import Path
import os, subprocess
root=Path(__file__).resolve().parents[1]
source=Path(os.environ.get('AUDIO_RECOVERY_SOURCE',root/'ios/Sources/CapacitorTwilioVoicePlugin/CapacitorTwilioVoicePlugin.swift')).read_text()
helper=(root/'ios/Sources/CapacitorTwilioVoicePlugin/AudioRecoveryState.swift').read_text()
fault=os.environ.get('AUDIO_RECOVERY_FAULT','')
if fault=='activation':source=source.replace('return AudioRecoveryFailure(phase: phase, error: error as NSError).diagnostic','_ = AudioRecoveryFailure(phase: phase, error: error as NSError).diagnostic')
if fault=='generation':helper=helper.replace('generation == capturedGeneration && permitsRecovery','permitsRecovery')
if fault=='mute':helper=helper.replace(' && !muted','')
if fault=='hold':helper=helper.replace(' && !held','')
if fault=='other':helper=helper.replace('otherCallKitCalls == 0 && ','')
if fault=='token':helper=helper.replace('tokenMatches && ','')
def method_named(name):
 start=source.index('    private func '+name+'(');i=source.index('{',start);j=i+1;depth=1
 while depth:
  if source[j]=='{':depth+=1
  elif source[j]=='}':depth-=1
  j+=1
 return source[start:j]
method=method_named('restartCallAudio')
if '    private func audioRecoveryCounts(' in source:
 method=method_named('audioRecoveryCounts')+'\n'+method_named('audioRecoveryState')+'\n'+method
# The actual Foundation-only helper and exact native method body are executed.
# Only the OS/device/call/queue boundary types below are invented.
stubs='''
struct QueueTime {static func now()->QueueTime{QueueTime()};static func +(a:QueueTime,b:Double)->QueueTime{a}}
final class ManualQueue {static let main=ManualQueue();var tasks:[()->Void]=[];func asyncAfter(deadline:QueueTime,execute:@escaping()->Void){tasks.append(execute)};func flush(){let t=tasks;tasks=[];t.forEach{$0()}}}
typealias DispatchQueue=ManualQueue
final class AVAudioSession {
 enum Category {case playAndRecord,other};enum Mode {case voiceChat,other};struct Options:OptionSet{let rawValue:Int;static let allowBluetooth=Options(rawValue:1);static let allowBluetoothA2DP=Options(rawValue:2);static let allowAirPlay=Options(rawValue:4)}
 static let shared=AVAudioSession();static func sharedInstance()->AVAudioSession{shared};var category:Category = .playAndRecord;var mode:Mode = .voiceChat;var failure:NSError?;var failCategory=false;var activations=0
 func setCategory(_ c:Category,mode:Mode,options:Options)throws{if failCategory,let failure=failure{throw failure};category=c;self.mode=mode}
 func setActive(_ active:Bool)throws{activations+=1;if let failure=failure{throw failure}}
}
final class AudioDevice {var writes:[Bool]=[];var isEnabled=false{didSet{writes.append(isEnabled)}}}
final class Call {enum State {case connected,disconnected};var uuid:UUID?;var state:State = .connected;var isOnHold=false;var isMuted=false}
struct ObservedCall {let uuid:UUID;var hasEnded=false}
final class CallObserver {var calls:[ObservedCall]=[]}
final class Invite {let uuid=UUID()}
final class CapacitorTwilioVoicePlugin {
 var audioSessionActive=false;var audioLifecycleGeneration=1;let audioDevice=AudioDevice();var lastSpeakerChoice=false;let uuid=UUID();let call=Call();var routes:[Bool]=[]
 var activeCalls:[String:Call]=[:];var activeCallInvites:[String:Invite]=[:];var pendingOutgoingCalls:[UUID:Bool]=[:];var watchdogTokens:[UUID:Int]=[:];let callObserver=CallObserver();var reportedCallKitUUIDs=Set<UUID>()
 var live=true{didSet{call.state=live ? .connected:.disconnected}};var token=1{didSet{watchdogTokens[uuid]=token}}
 var others=0{didSet{callObserver.calls=(0..<others).map{_ in ObservedCall(uuid:UUID())}}}
 var pluginOthers=0{didSet{activeCallInvites=[:];for i in 0..<pluginOthers{activeCallInvites[String(i)]=Invite()}}}
 init(){call.uuid=uuid;activeCalls[uuid.uuidString]=call;watchdogTokens[uuid]=token}
 func liveWatchdogCall(token:Int,uuid:UUID)->Call?{live && token==self.token && uuid==self.uuid ? call:nil}
 func toggleAudioRoute(toSpeaker:Bool){routes.append(toSpeaker)}
 func run()->Any?{restartCallAudio(token:token,uuid:uuid)}
'''
tests='''
}
let session=AVAudioSession.shared
let osError=NSError(domain:"InventedOSDomain",code:12345,userInfo:[NSLocalizedDescriptionKey:"PRIVATE description", "PRIVATE": "userInfo secret"])
session.failure=osError
let failed=CapacitorTwilioVoicePlugin();let failure=failed.run();assert(ManualQueue.main.tasks.isEmpty,"failed activation must not schedule re-enable");assert(failed.audioDevice.writes.isEmpty,"failed activation must not toggle graph");let fields=failure as! [String:Any];assert(fields["errorDomain"] as? String == "InventedOSDomain");assert(fields["errorCode"] as? Int == 12345);assert(fields["phase"] as? String == "set-active");assert(!String(describing:fields).contains("PRIVATE"));assert(!failed.audioSessionActive)
session.failCategory=true;session.category = .other;let category=CapacitorTwilioVoicePlugin();let categoryFields=category.run() as! [String:Any];assert(categoryFields["phase"] as? String == "set-category");assert(category.audioDevice.writes.isEmpty);session.failCategory=false;session.category = .playAndRecord
session.failure=nil
let healthy=CapacitorTwilioVoicePlugin();let requested=healthy.run() as! [String:Any];assert(requested["action"] as? String == "restart-requested");assert(!healthy.audioSessionActive,"activation request alone is not CallKit callback readiness");ManualQueue.main.flush();assert(healthy.audioDevice.isEnabled);assert(healthy.routes==[false])
for mode in ["end","replace","hold","mute","deactivate","other","plugin-other"] {
 let p=CapacitorTwilioVoicePlugin();_ = p.run();assert(ManualQueue.main.tasks.count==1)
 switch mode {case "end":p.live=false;case "replace":p.token+=1;case "hold":p.call.isOnHold=true;case "mute":p.call.isMuted=true;case "deactivate":p.audioLifecycleGeneration+=1;case "other":p.others=1;default:p.pluginOthers=1}
 ManualQueue.main.flush();assert(!p.audioDevice.isEnabled,"delayed guard must preserve \\(mode)");assert(p.routes.isEmpty)
}
for other in [true,false] {let p=CapacitorTwilioVoicePlugin();if other{p.others=1}else{p.pluginOthers=1};let before=session.activations;let result=p.run() as! [String:Any];assert(result["action"] as? String == "deferred-other-state");assert(session.activations==before,"no forced activation with real other call");assert(p.audioDevice.writes.isEmpty);assert(ManualQueue.main.tasks.isEmpty)}
let activated=CapacitorTwilioVoicePlugin();_ = activated.run();activated.audioLifecycleGeneration+=1;activated.audioDevice.isEnabled=true;ManualQueue.main.flush();assert(activated.audioDevice.isEnabled);assert(activated.routes.isEmpty,"old delayed recovery must not override new callback")
let counts=CapacitorTwilioVoicePlugin();counts.others=2;counts.reportedCallKitUUIDs.insert(counts.callObserver.calls[0].uuid);let firstCounts=counts.counts();assert(firstCounts["otherOwnCalls"] as? Int == 1);assert(firstCounts["otherExternalCalls"] as? Int == 1);let pending=CapacitorTwilioVoicePlugin();pending.pendingOutgoingCalls[UUID()]=true;let beforePending=session.activations;_ = pending.run();assert(session.activations==beforePending)
print("PASS actual Swift recovery and pure policy: activation/category errors retain code+phase without userInfo and never toggle; lifecycle/end/replace/hold/mute/real-other guards; success requests, never claims audible readiness")
'''
work=Path(os.environ.get('AUDIO_RECOVERY_OUTPUT',str(root/'work/audio-recovery-check')));work.mkdir(parents=True,exist_ok=True)
harness=work/('recovery-'+(fault or ('baseline' if os.environ.get('AUDIO_RECOVERY_SOURCE') else 'green'))+'.swift')
if '    private func audioRecoveryCounts(' not in source:
 tests=tests[:tests.index('let counts=CapacitorTwilioVoicePlugin()')]+'print(\"baseline reached unexpected end\")\n'
harness.write_text(helper+stubs+(('    func counts()->[String:Any]{audioRecoveryCounts(for:uuid)}\n') if '    private func audioRecoveryCounts(' in source else '')+method+tests)
r=subprocess.run(['swift',str(harness)],text=True,capture_output=True)
print(r.stdout,end='');print(r.stderr,end='');raise SystemExit(r.returncode)
