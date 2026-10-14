# Diagrams

Editable **`.drawio.svg`** files: they display as images in the notes, and open for editing in VS Code (Draw.io Integration extension) or [app.diagrams.net](https://app.diagrams.net). Simpler diagrams live inside the lessons as **Mermaid** code blocks, which GitHub renders directly.

The file names keep the numbers of the notes they were drawn for before the reorganisation; they're not module numbers.

| Diagram | Shows | Used in |
|---|---|---|
| [00-building-story.drawio.svg](00-building-story.drawio.svg) | Docker networking as an apartment building: flats, corridor, doors, reception | [Level 10](../10-container-and-kubernetes-networking/README.md) |
| [02-netfilter-chains.drawio.svg](02-netfilter-chains.drawio.svg) | The five netfilter hooks a packet passes on a Linux host | [8.6](../08-linux-networking/06-netfilter-nat-and-conntrack.md) |
| [04-dns-journey.drawio.svg](04-dns-journey.drawio.svg) | A DNS lookup from the client to the authoritative server | [3.4](../03-core-networking-protocols/04-dns.md) |
| [06-debug-ladder.drawio.svg](06-debug-ladder.drawio.svg) | The 6-step troubleshooting method | [3.11](../03-core-networking-protocols/11-troubleshooting-connectivity.md) |
| [08-osi-layers.drawio.svg](08-osi-layers.drawio.svg) | The 7 OSI layers and the TCP/IP model | [1.5](../01-networking-fundamentals/05-osi-and-tcp-ip-models.md) |
| [08-osi-encapsulation.drawio.svg](08-osi-encapsulation.drawio.svg) | Encapsulation: headers added on the way down | [1.5](../01-networking-fundamentals/05-osi-and-tcp-ip-models.md) |

Two diagrams in the Docker notes are used here too: [the bridge network](../../docker/diagrams/08-bridge-network.drawio.svg) and [the packet's journey](../../docker/diagrams/08-packet-flow.drawio.svg) (both in [10.1](../10-container-and-kubernetes-networking/01-docker-bridge-networking-inside-out.md)).

**To redraw on a whiteboard in an interview:** the packet's journey, the debug ladder and the OSI layer stack.
