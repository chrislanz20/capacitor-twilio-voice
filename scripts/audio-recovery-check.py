"""Execute actual native methods at invented Foundation-only OS/call boundaries.
No iOS hardware, provider, credentials or network. BASELINE_PARITY=1 executes
healthy controls only, allowing exact behavioral comparison against build275.
AUDIO_RECOVERY_SOURCE selects baseline source. Faults mutate memory only.
"""
from pathlib import Path
import os, subprocess
root=Path(__file__).resolve().parents[1]
source=Path(os.environ.get('AUDIO_RECOVERY_SOURCE',root/'ios/Sources/CapacitorTwilioVoicePlugin/CapacitorTwilioVoicePlugin.swift')).read_text()
helper=(root/'ios/Sources/CapacitorTwilioVoicePlugin/AudioRecoveryState.swift').read_text()
fault=os.environ.get('AUDIO_RECOVERY_FAULT','')
if fault=='activation': source=source.replace('return AudioRecoveryFailure(phase: phase, error: error as NSError).diagnostic','_ = AudioRecoveryFailure(phase: phase, error: error as NSError).diagnostic')
if fault=='token': source=source.replace('guard watchdogTokens[uuid] == token,','guard true,')
if fault=='hold': source=source.replace('!call.isOnHold else { return }','true else { return }')
if fault=='mute-cancel': source=source.replace('!call.isOnHold else { return }','!call.isOnHold, !call.isMuted else { return }')
if fault=='active-flag': source=source.replace('            audioSessionActive = true','            // removed internal state')
def extract(marker):
 start=source.index(marker);i=source.index('{',start);j=i+1;depth=1
 while depth:
  if source[j]=='{':depth+=1
  elif source[j]=='}':depth-=1
  j+=1
 return source[start:j].replace('public func','func')
methods='\n'.join(extract(m) for m in ['    private func liveWatchdogCall(', '    private func restartCallAudio(', '    public func provider(_ provider: CXProvider, perform action: CXSetMutedCallAction)', '    public func provider(_ provider: CXProvider, didActivate audioSession: AVAudioSession)', '    public func provider(_ provider: CXProvider, didDeactivate audioSession: AVAudioSession)', '    public func providerDidReset('])
if '    private func audioRecoveryCounts(' in source: methods+= '\n'+extract('    private func audioRecoveryCounts(')
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
class CXProvider {}
class CXSetMutedCallAction {let callUUID:UUID;let isMuted:Bool;var fulfilled=false;init(_ id:UUID,_ value:Bool){callUUID=id;isMuted=value};func fulfill(){fulfilled=true};func fail(){}}
final class CapacitorTwilioVoicePlugin {
 var audioSessionActive=false;var audioLifecycleGeneration=0;let audioDevice=AudioDevice();var lastSpeakerChoice=false;let uuid=UUID();let call=Call();var routes:[Bool]=[]
 var activeCalls:[String:Call]=[:];var activeCallInvites:[String:Invite]=[:];var pendingOutgoingCalls:[UUID:Bool]=[:];var watchdogTokens:[UUID:Int]=[:];let callObserver=CallObserver();var reportedCallKitUUIDs=Set<UUID>()
 init(){call.uuid=uuid;activeCalls[uuid.uuidString]=call;watchdogTokens[uuid]=1}
 func toggleAudioRoute(toSpeaker:Bool){routes.append(toSpeaker)}
 func notifyListeners(_ event:String,data:[String:Any]?){}
 func currentTwilioSid()->String?{nil};func updateProximityMonitoring(){}
 func run()->Any?{restartCallAudio(token:1,uuid:uuid)}
'''
healthy='''
}
let session=AVAudioSession.shared
var snapshots:[[String:Any]]=[]
for mode in ["normal","mute","mute-unmute","end","replace","hold","deactivate","reactivate","reset","other","invite","route"] {
 let p=CapacitorTwilioVoicePlugin();_ = p.run();assert(p.audioSessionActive,"preserve baseline internal activation flag");assert(ManualQueue.main.tasks.count==1)
 switch mode {
 case "mute","mute-unmute":p.provider(CXProvider(),perform:CXSetMutedCallAction(p.uuid,true))
 case "end":p.call.state = .disconnected
 case "replace":p.watchdogTokens[p.uuid]=2
 case "hold":p.call.isOnHold=true
 case "deactivate":p.provider(CXProvider(),didDeactivate:session)
 case "reactivate":p.provider(CXProvider(),didDeactivate:session);p.provider(CXProvider(),didActivate:session)
 case "reset":p.providerDidReset(CXProvider())
 case "other":p.callObserver.calls=[ObservedCall(uuid:UUID())]
 case "invite":p.activeCallInvites["invented"]=Invite()
 case "route":p.lastSpeakerChoice=true
 default:break
 }
 ManualQueue.main.flush()
 if mode == "mute-unmute" {p.provider(CXProvider(),perform:CXSetMutedCallAction(p.uuid,false))}
 if ["end","replace","hold"].contains(mode){assert(!p.audioDevice.isEnabled,"baseline guard \\(mode)")}
 else {assert(p.audioDevice.isEnabled,"same live call must not be stranded by \\(mode)")}
 if mode == "mute" {assert(p.call.isMuted,"graph enable must not unmute call")}
 if mode == "mute-unmute" {assert(!p.call.isMuted)}
 snapshots.append(["mode":mode,"writes":p.audioDevice.writes,"routes":p.routes,"muted":p.call.isMuted,"active":p.audioSessionActive])
}
let json=try! JSONSerialization.data(withJSONObject:snapshots,options:[.sortedKeys]);print("PARITY "+String(data:json,encoding:.utf8)!)
'''
failures='''
let osError=NSError(domain:"InventedOSDomain",code:12345,userInfo:[NSLocalizedDescriptionKey:"PRIVATE description", "PRIVATE": "userInfo secret"])
for categoryFailure in [false,true] {
 session.failure=osError;session.failCategory=categoryFailure;session.category = categoryFailure ? .other:.playAndRecord
 let p=CapacitorTwilioVoicePlugin();let result=p.run();assert(ManualQueue.main.tasks.isEmpty,"failed activation must not schedule re-enable");assert(p.audioDevice.writes.isEmpty,"failed activation must not toggle graph")
 let fields=result as! [String:Any];assert(fields["errorDomain"] as? String == "InventedOSDomain");assert(fields["errorCode"] as? Int == 12345);assert(fields["phase"] as? String == (categoryFailure ? "set-category":"set-active"));assert(!String(describing:fields).contains("PRIVATE"));assert(!p.audioSessionActive)
}
let bounded=AudioRecoveryFailure(phase:"set-active",error:NSError(domain:String(repeating:"A",count:200),code:-50)).diagnostic;assert((bounded["errorDomain"] as! String).count==96)
print("PASS actual methods: category/activation early return, structured private error boundary, baseline internal flag, actual CX mute/unmute callbacks and lifecycle controls")
'''
work=Path(os.environ.get('AUDIO_RECOVERY_OUTPUT',str(root/'work/audio-recovery-check')));work.mkdir(parents=True,exist_ok=True)
harness=work/('recovery-'+(fault or ('parity' if os.environ.get('BASELINE_PARITY') else 'green'))+'.swift')
harness.write_text(helper+stubs+methods+healthy+('' if os.environ.get('BASELINE_PARITY') else failures))
r=subprocess.run(['swift',str(harness)],text=True,capture_output=True)
print(r.stdout,end='');print(r.stderr,end='');raise SystemExit(r.returncode)
