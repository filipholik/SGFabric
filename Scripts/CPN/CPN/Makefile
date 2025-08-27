TARGETS:=switch functions-src
ifdef DPDK
	TARGETS:=dpdkswitch-src
endif

all: $(TARGETS)

bpfmap-src:
	cd bpfmap && $(MAKE)

protocol-src:
	cd protocol && $(MAKE)

ubpf-src: bpfmap-src
	cd ubpf && $(MAKE)

agent-src: protocol-src bpfmap-src ubpf-src
	cd COMML/agent && $(MAKE)

switch: agent-src
	cd COMML/softswitch && $(MAKE)

dpdkswitch-src: agent-src
	cd COMML/dpdkswitch && $(MAKE)

functions-src:
	cd functions && $(MAKE)

clean:
	cd bpfmap && $(MAKE) clean
	cd ubpf && $(MAKE) clean
	cd COMML/agent && $(MAKE) clean
	cd protocol && $(MAKE) clean
	cd COMML/softswitch && $(MAKE) clean
	cd functions && $(MAKE) clean

ifdef DPDK
  cd COMML/dpdkswitch && $(MAKE) clean
endif
