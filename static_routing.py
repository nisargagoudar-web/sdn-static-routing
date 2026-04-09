from pox.core import core
from pox.lib.util import dpidToStr
import pox.openflow.libopenflow_01 as of

log = core.getLogger()

# MAC addresses of hosts (we'll fill these after first run)
# Topology: H1--S1--S2--H3
#                |
#               S3
#                |
#               H2

def install_flow(connection, src_mac, dst_mac, out_port):
    msg = of.ofp_flow_mod()
    msg.match.dl_src = src_mac
    msg.match.dl_dst = dst_mac
    msg.actions.append(of.ofp_action_output(port=out_port))
    connection.send(msg)
    log.info(f"Flow installed: {src_mac} -> {dst_mac} out port {out_port}")

class StaticRoutingController(object):
    def __init__(self):
        core.openflow.addListeners(self)

    def _handle_ConnectionUp(self, event):
        dpid = event.dpid
        log.info(f"Switch connected: {dpidToStr(dpid)}")

    def _handle_PacketIn(self, event):
        packet = event.parsed
        log.info(f"PacketIn from switch {dpidToStr(event.dpid)}: "
                 f"{packet.src} -> {packet.dst} on port {event.port}")

        # Flood packet so we can see MACs in logs first
        msg = of.ofp_packet_out()
        msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
        msg.data = event.ofp
        event.connection.send(msg)

def launch():
    core.registerNew(StaticRoutingController)
