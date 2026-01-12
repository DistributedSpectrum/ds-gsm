#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Not titled yet
# Author: subrad
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5 import QtCore
from gnuradio import audio
from gnuradio import blocks
import pmt
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import gr, pdu
from gnuradio import gsm
from gnuradio import network
from gnuradio import vocoder
import bladeRF
import time
import sip
import threading



class get_tch_bladerf(gr.top_block, Qt.QWidget):

    def __init__(self, fc=937e6, input_file_name="../test_data/gsm_test_voice_call.sigmf-data", osr=4, rx_gain=20, samp_rate_in=(100.0e6/174.0), serial_id="", sigmf_enable=0):
        gr.top_block.__init__(self, "Not titled yet", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Not titled yet")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "get_tch_bladerf")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)
        self.flowgraph_started = threading.Event()

        ##################################################
        # Parameters
        ##################################################
        self.fc = fc
        self.input_file_name = input_file_name
        self.osr = osr
        self.rx_gain = rx_gain
        self.samp_rate_in = samp_rate_in
        self.serial_id = serial_id
        self.sigmf_enable = sigmf_enable

        ##################################################
        # Variables
        ##################################################
        self.sigmf_file_replay = sigmf_file_replay = sigmf_enable
        self.sdr_gain = sdr_gain = rx_gain
        self.input_sigmf_entry = input_sigmf_entry = input_file_name
        self.input_sigmf = input_sigmf = "../test_data/sms_downlink_tail"
        self.input_rx_freq = input_rx_freq = fc

        ##################################################
        # Blocks
        ##################################################

        _sigmf_file_replay_check_box = Qt.QCheckBox("Enable SigMF file replay")
        self._sigmf_file_replay_choices = {True: True, False: False}
        self._sigmf_file_replay_choices_inv = dict((v,k) for k,v in self._sigmf_file_replay_choices.items())
        self._sigmf_file_replay_callback = lambda i: Qt.QMetaObject.invokeMethod(_sigmf_file_replay_check_box, "setChecked", Qt.Q_ARG("bool", self._sigmf_file_replay_choices_inv[i]))
        self._sigmf_file_replay_callback(self.sigmf_file_replay)
        _sigmf_file_replay_check_box.stateChanged.connect(lambda i: self.set_sigmf_file_replay(self._sigmf_file_replay_choices[bool(i)]))
        self.top_grid_layout.addWidget(_sigmf_file_replay_check_box, 0, 7, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(7, 8):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._sdr_gain_range = qtgui.Range((-16), 60, 1, rx_gain, 200)
        self._sdr_gain_win = qtgui.RangeWidget(self._sdr_gain_range, self.set_sdr_gain, "'sdr_gain'", "counter_slider", int, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._sdr_gain_win, 1, 3, 1, 3)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(3, 6):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._input_sigmf_entry_tool_bar = Qt.QToolBar(self)
        self._input_sigmf_entry_tool_bar.addWidget(Qt.QLabel("SigMF Data filepath" + ": "))
        self._input_sigmf_entry_line_edit = Qt.QLineEdit(str(self.input_sigmf_entry))
        self._input_sigmf_entry_tool_bar.addWidget(self._input_sigmf_entry_line_edit)
        self._input_sigmf_entry_line_edit.editingFinished.connect(
            lambda: self.set_input_sigmf_entry(str(str(self._input_sigmf_entry_line_edit.text()))))
        self.top_grid_layout.addWidget(self._input_sigmf_entry_tool_bar, 0, 0, 1, 6)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 6):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._input_rx_freq_tool_bar = Qt.QToolBar(self)
        self._input_rx_freq_tool_bar.addWidget(Qt.QLabel("RX Center Freq " + ": "))
        self._input_rx_freq_line_edit = Qt.QLineEdit(str(self.input_rx_freq))
        self._input_rx_freq_tool_bar.addWidget(self._input_rx_freq_line_edit)
        self._input_rx_freq_line_edit.editingFinished.connect(
            lambda: self.set_input_rx_freq(eng_notation.str_to_num(str(self._input_rx_freq_line_edit.text()))))
        self.top_grid_layout.addWidget(self._input_rx_freq_tool_bar, 1, 0, 1, 3)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.vocoder_gsm_fr_decode_ps_0 = vocoder.gsm_fr_decode_ps()
        self.qtgui_time_sink_x_0 = qtgui.time_sink_c(
            (4096*64), #size
            samp_rate_in, #samp_rate
            'Max IQ value Stream (scaled by 2048)', #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_0.set_update_time(0.08)
        self.qtgui_time_sink_x_0.set_y_axis(0, 1)

        self.qtgui_time_sink_x_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0.enable_tags(True)
        self.qtgui_time_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0.enable_autoscale(False)
        self.qtgui_time_sink_x_0.enable_grid(True)
        self.qtgui_time_sink_x_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0.enable_control_panel(False)
        self.qtgui_time_sink_x_0.enable_stem_plot(False)


        labels = ['I', 'Q', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(2):
            if len(labels[i]) == 0:
                if (i % 2 == 0):
                    self.qtgui_time_sink_x_0.set_line_label(i, "Re{{Data {0}}}".format(i/2))
                else:
                    self.qtgui_time_sink_x_0.set_line_label(i, "Im{{Data {0}}}".format(i/2))
            else:
                self.qtgui_time_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_time_sink_x_0_win, 9, 0, 1, 6)
        for r in range(9, 10):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 6):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_freq_sink_x_0 = qtgui.freq_sink_c(
            1024, #size
            window.WIN_HANN, #wintype
            0, #fc
            samp_rate_in, #bw
            "", #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_x_0.set_update_time(0.10)
        self.qtgui_freq_sink_x_0.set_y_axis((-120), 10)
        self.qtgui_freq_sink_x_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_0.enable_grid(False)
        self.qtgui_freq_sink_x_0.set_fft_average(0.2)
        self.qtgui_freq_sink_x_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0.enable_control_panel(True)
        self.qtgui_freq_sink_x_0.set_fft_window_normalized(False)



        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_0.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_freq_sink_x_0_win, 2, 0, 1, 6)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 6):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.pdu_pdu_to_tagged_stream_0 = pdu.pdu_to_tagged_stream(gr.types.byte_t, 'packet_len')
        self.network_socket_pdu_1 = network.socket_pdu('UDP_SERVER', '127.0.0.1', '4729', 10000, False)
        self.network_socket_pdu_0 = network.socket_pdu('UDP_CLIENT', '127.0.0.1', '4729', 10000, False)
        self.gsm_tch_f_decoder_0 = gsm.tch_f_decoder(gsm.TCH_FS, True)
        self.gsm_tch_f_chans_demapper_0 = gsm.tch_f_chans_demapper(5)
        self.gsm_receiver_1 = gsm.receiver(4, [0], [], False)
        self.gsm_message_printer_0_1 = gsm.message_printer(pmt.intern(""), False,
            False, False)
        self.gsm_message_printer_0 = gsm.message_printer(pmt.intern(""), False,
            False, False)
        self.gsm_input_1 = gsm.gsm_input(
            ppm=0,
            osr=osr,
            fc=fc,
            samp_rate_in=samp_rate_in,
        )
        self.gsm_decryption_0_0_0_0 = gsm.decryption([0x1e, 0xf0, 0x0b, 0xab, 0x3b, 0xac, 0x70, 0x02], 1)
        self.gsm_decryption_0_0_0 = gsm.decryption([0x1e, 0xf0, 0x0b, 0xab, 0x3b, 0xac, 0x70, 0x02], 1)
        self.gsm_control_channels_decoder_0 = gsm.control_channels_decoder()
        self.gsm_clock_offset_control_1 = gsm.clock_offset_control(fc, samp_rate_in, osr)
        self.blocks_throttle2_1 = blocks.throttle( gr.sizeof_gr_complex*1, samp_rate_in, True, 0 if "auto" == "auto" else max( int(float(0.1) * samp_rate_in) if "auto" == "time" else int(0.1), 1) )
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_char*1, 33)
        self.blocks_sigmf_source_minimal_0 = blocks.file_source(gr.sizeof_short, input_sigmf_entry, True, 0, 0)
        self.blocks_sigmf_source_minimal_0.set_begin_tag(pmt.PMT_NIL)
        self.blocks_short_to_float_0 = blocks.short_to_float(1, 32767.0)
        self.blocks_selector_0 = blocks.selector(gr.sizeof_gr_complex*1,sigmf_file_replay,0)
        self.blocks_selector_0.set_enabled(True)
        self.blocks_interleaved_short_to_complex_0_0_0 = blocks.interleaved_short_to_complex(False, False,2047.0)
        self.blocks_interleaved_short_to_complex_0 = blocks.interleaved_short_to_complex(False, False,2047)
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_char*1, 'out.gsm', False)
        self.blocks_file_sink_0.set_unbuffered(False)
        self.blocks_complex_to_interleaved_short_1 = blocks.complex_to_interleaved_short(False,2047)
        self.blocks_abs_xx_0_0 = blocks.abs_ss(1)
        self.bladeRF_source_0 = bladeRF.source(
            args="numchan=" + str(1)
                 + ",metadata=" + 'False'
                 + ",bladerf=" +  str(serial_id)
                 + ",verbosity=" + 'verbose'
                 + ",feature=" + 'default'
                 + ",sample_format=" + '16bit'
                 + ",fpga=" + str('')
                 + ",fpga-reload=" + 'False'
                 + ",use_ref_clk=" + 'False'
                 + ",ref_clk=" + str(int(10e6))
                 + ",buflen=" + str(int(4096))
                 + ",buffers=" + str(int(512))
                 + ",in_clk=" + 'ONBOARD'
                 + ",out_clk=" + str(False)
                 + ",use_dac=" + 'False'
                 + ",dac=" + str(10000)
                 + ",xb200=" + 'none'
                 + ",tamer=" + 'internal'
                 + ",sampling=" + 'internal'
                 + ",lpf_mode="+'disabled'
                 + ",smb="+str(int(38.4e6))
                 + ",dc_calibration="+'LPF_TUNING'
                 + ",trigger0="+'False'
                 + ",trigger_role0="+'master'
                 + ",trigger_signal0="+'J51_1'
                 + ",trigger1="+'False'
                 + ",trigger_role1="+'master'
                 + ",trigger_signal1="+'J51_1'
                 + ",bias_tee0="+'False'
                 + ",bias_tee1="+'False'


        )
        self.bladeRF_source_0.set_sample_rate(samp_rate_in)
        self.bladeRF_source_0.set_center_freq(input_rx_freq,0)
        self.bladeRF_source_0.set_bandwidth(samp_rate_in,0)
        self.bladeRF_source_0.set_dc_offset_mode(0, 0)
        self.bladeRF_source_0.set_iq_balance_mode(0, 0)
        self.bladeRF_source_0.set_gain_mode(False, 0)
        self.bladeRF_source_0.set_gain(sdr_gain, 0)
        self.bladeRF_source_0.set_if_gain(sdr_gain, 0)
        self.audio_sink_0 = audio.sink(8000, '', True)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.gsm_clock_offset_control_1, 'ctrl'), (self.gsm_input_1, 'ctrl_in'))
        self.msg_connect((self.gsm_control_channels_decoder_0, 'msgs'), (self.gsm_message_printer_0, 'msgs'))
        self.msg_connect((self.gsm_control_channels_decoder_0, 'msgs'), (self.network_socket_pdu_0, 'pdus'))
        self.msg_connect((self.gsm_decryption_0_0_0, 'bursts'), (self.gsm_tch_f_decoder_0, 'bursts'))
        self.msg_connect((self.gsm_decryption_0_0_0_0, 'bursts'), (self.gsm_control_channels_decoder_0, 'bursts'))
        self.msg_connect((self.gsm_receiver_1, 'measurements'), (self.gsm_clock_offset_control_1, 'measurements'))
        self.msg_connect((self.gsm_receiver_1, 'C0'), (self.gsm_tch_f_chans_demapper_0, 'bursts'))
        self.msg_connect((self.gsm_tch_f_chans_demapper_0, 'tch_bursts'), (self.gsm_decryption_0_0_0, 'bursts'))
        self.msg_connect((self.gsm_tch_f_chans_demapper_0, 'acch_bursts'), (self.gsm_decryption_0_0_0_0, 'bursts'))
        self.msg_connect((self.gsm_tch_f_decoder_0, 'msgs'), (self.gsm_message_printer_0_1, 'msgs'))
        self.msg_connect((self.gsm_tch_f_decoder_0, 'msgs'), (self.network_socket_pdu_0, 'pdus'))
        self.msg_connect((self.gsm_tch_f_decoder_0, 'voice'), (self.pdu_pdu_to_tagged_stream_0, 'pdus'))
        self.connect((self.bladeRF_source_0, 0), (self.blocks_selector_0, 0))
        self.connect((self.blocks_abs_xx_0_0, 0), (self.blocks_interleaved_short_to_complex_0, 0))
        self.connect((self.blocks_complex_to_interleaved_short_1, 0), (self.blocks_abs_xx_0_0, 0))
        self.connect((self.blocks_interleaved_short_to_complex_0, 0), (self.qtgui_time_sink_x_0, 0))
        self.connect((self.blocks_interleaved_short_to_complex_0_0_0, 0), (self.blocks_throttle2_1, 0))
        self.connect((self.blocks_selector_0, 0), (self.blocks_complex_to_interleaved_short_1, 0))
        self.connect((self.blocks_selector_0, 0), (self.gsm_input_1, 0))
        self.connect((self.blocks_selector_0, 0), (self.qtgui_freq_sink_x_0, 0))
        self.connect((self.blocks_short_to_float_0, 0), (self.audio_sink_0, 0))
        self.connect((self.blocks_sigmf_source_minimal_0, 0), (self.blocks_interleaved_short_to_complex_0_0_0, 0))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.vocoder_gsm_fr_decode_ps_0, 0))
        self.connect((self.blocks_throttle2_1, 0), (self.blocks_selector_0, 1))
        self.connect((self.gsm_input_1, 0), (self.gsm_receiver_1, 0))
        self.connect((self.pdu_pdu_to_tagged_stream_0, 0), (self.blocks_file_sink_0, 0))
        self.connect((self.pdu_pdu_to_tagged_stream_0, 0), (self.blocks_stream_to_vector_0, 0))
        self.connect((self.vocoder_gsm_fr_decode_ps_0, 0), (self.blocks_short_to_float_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "get_tch_bladerf")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_fc(self):
        return self.fc

    def set_fc(self, fc):
        self.fc = fc
        self.set_input_rx_freq(self.fc)
        self.gsm_clock_offset_control_1.set_fc(self.fc)
        self.gsm_input_1.set_fc(self.fc)

    def get_input_file_name(self):
        return self.input_file_name

    def set_input_file_name(self, input_file_name):
        self.input_file_name = input_file_name
        self.set_input_sigmf_entry(self.input_file_name)

    def get_osr(self):
        return self.osr

    def set_osr(self, osr):
        self.osr = osr
        self.gsm_input_1.set_osr(self.osr)

    def get_rx_gain(self):
        return self.rx_gain

    def set_rx_gain(self, rx_gain):
        self.rx_gain = rx_gain
        self.set_sdr_gain(self.rx_gain)

    def get_samp_rate_in(self):
        return self.samp_rate_in

    def set_samp_rate_in(self, samp_rate_in):
        self.samp_rate_in = samp_rate_in
        self.bladeRF_source_0.set_sample_rate(self.samp_rate_in)
        self.bladeRF_source_0.set_bandwidth(self.samp_rate_in, 0)
        self.blocks_throttle2_1.set_sample_rate(self.samp_rate_in)
        self.gsm_input_1.set_samp_rate_in(self.samp_rate_in)
        self.qtgui_freq_sink_x_0.set_frequency_range(0, self.samp_rate_in)
        self.qtgui_time_sink_x_0.set_samp_rate(self.samp_rate_in)

    def get_serial_id(self):
        return self.serial_id

    def set_serial_id(self, serial_id):
        self.serial_id = serial_id

    def get_sigmf_enable(self):
        return self.sigmf_enable

    def set_sigmf_enable(self, sigmf_enable):
        self.sigmf_enable = sigmf_enable
        self.set_sigmf_file_replay(self.sigmf_enable)

    def get_sigmf_file_replay(self):
        return self.sigmf_file_replay

    def set_sigmf_file_replay(self, sigmf_file_replay):
        self.sigmf_file_replay = sigmf_file_replay
        self._sigmf_file_replay_callback(self.sigmf_file_replay)
        self.blocks_selector_0.set_input_index(self.sigmf_file_replay)

    def get_sdr_gain(self):
        return self.sdr_gain

    def set_sdr_gain(self, sdr_gain):
        self.sdr_gain = sdr_gain
        self.bladeRF_source_0.set_gain(self.sdr_gain, 0)
        self.bladeRF_source_0.set_if_gain(self.sdr_gain, 0)

    def get_input_sigmf_entry(self):
        return self.input_sigmf_entry

    def set_input_sigmf_entry(self, input_sigmf_entry):
        self.input_sigmf_entry = input_sigmf_entry
        Qt.QMetaObject.invokeMethod(self._input_sigmf_entry_line_edit, "setText", Qt.Q_ARG("QString", str(self.input_sigmf_entry)))
        self.blocks_sigmf_source_minimal_0.open(self.input_sigmf_entry, True)

    def get_input_sigmf(self):
        return self.input_sigmf

    def set_input_sigmf(self, input_sigmf):
        self.input_sigmf = input_sigmf

    def get_input_rx_freq(self):
        return self.input_rx_freq

    def set_input_rx_freq(self, input_rx_freq):
        self.input_rx_freq = input_rx_freq
        Qt.QMetaObject.invokeMethod(self._input_rx_freq_line_edit, "setText", Qt.Q_ARG("QString", eng_notation.num_to_str(self.input_rx_freq)))
        self.bladeRF_source_0.set_center_freq(self.input_rx_freq, 0)



def argument_parser():
    parser = ArgumentParser()
    parser.add_argument(
        "--fc", dest="fc", type=eng_float, default=eng_notation.num_to_str(float(937e6)),
        help="Set fc [default=%(default)r]")
    parser.add_argument(
        "-i", "--input-file-name", dest="input_file_name", type=str, default="../test_data/gsm_test_voice_call.sigmf-data",
        help="Set input_file_name [default=%(default)r]")
    parser.add_argument(
        "--osr", dest="osr", type=intx, default=4,
        help="Set OSR [default=%(default)r]")
    parser.add_argument(
        "-g", "--rx-gain", dest="rx_gain", type=intx, default=20,
        help="Set gain [default=%(default)r]")
    parser.add_argument(
        "--samp-rate-in", dest="samp_rate_in", type=eng_float, default=eng_notation.num_to_str(float((100.0e6/174.0))),
        help="Set fs [default=%(default)r]")
    parser.add_argument(
        "-s", "--serial-id", dest="serial_id", type=str, default="",
        help="Set serial [default=%(default)r]")
    parser.add_argument(
        "-e", "--sigmf-enable", dest="sigmf_enable", type=intx, default=0,
        help="Set sigmf_enable [default=%(default)r]")
    return parser


def main(top_block_cls=get_tch_bladerf, options=None):
    if options is None:
        options = argument_parser().parse_args()

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls(fc=options.fc, input_file_name=options.input_file_name, osr=options.osr, rx_gain=options.rx_gain, samp_rate_in=options.samp_rate_in, serial_id=options.serial_id, sigmf_enable=options.sigmf_enable)

    tb.start()
    tb.flowgraph_started.set()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
