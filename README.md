# ds-gsm

User [bkerler's gr-gsm fork](https://github.com/bkerler/gr-gsm) for GNURadio 3.10 compatibility. Split for DS flowgraphs using bladeRF/SigMF  

## Dependencies

[GNURadio 3.10.12](https://github.com/gnuradio/gnuradio/tree/v3.10.12.0)
[libosmocore tag v1.12.1](https://github.com/osmocom/libosmocore/tree/1.12.1) -- [Install from source instructions](https://osmocom.org/projects/libosmocore/wiki/Libosmocore)
Source and Sink blocks that give most control over bladeRF: [gr-bladeRF](https://github.com/Nuand/gr-bladeRF)
Source and Sink blocks for generic SDR control. Works with bladeRF: [gr-osmosdr tag v0.2.6](https://github.com/osmocom/gr-osmosdr/tree/v0.2.6)

## The gr-gsm project

The *gr-gsm* project is based on the *gsm-receiver* written by Piotr Krysik (also the main author of *gr-gsm*) for the *Airprobe* project.

The aim is to provide a set of tools for receiving information transmitted by GSM equipment/devices.

### Installation and usage

Please see project's [wiki](https://osmocom.org/projects/gr-gsm/wiki/index) for information on [installation](https://osmocom.org/projects/gr-gsm/wiki/Installation) and [usage](https://github.com/ptrkrysik/gr-gsm/wiki/Usage) of gr-gsm.

