1. one oslo_messaging server will setup 3 queues:
   * aaaaaaa: queue name is topic, all server listens on this queue with roundrobin rule
   * aaaaaaa.server-0: queue name is topic + server (all in Target class), only server (server configured with server name in Target) listens on this queue that can receive this message
   * aaaaaaa_fanout_4664d1f0f6ca4b0e807ac3b1f8cc98c8: queue name is topic + fanout + random-uuid, all listener on this topic receive messages
   
