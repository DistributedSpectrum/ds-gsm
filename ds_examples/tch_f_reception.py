#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Tch F Reception
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5 import QtCore
from gnuradio import audio
from gnuradio import blocks
import pmt
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
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



class tch_f_reception(gr.top_block, Qt.QWidget):

    def __init__(self, fc=937e6, osr=4, samp_rate=(100.0e6/174.0)):
        gr.top_block.__init__(self, "Tch F Reception", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Tch F Reception")
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

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "tch_f_reception")

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
        self.osr = osr
        self.samp_rate = samp_rate

        ##################################################
        # Variables
        ##################################################
        self.tx_gain = tx_gain = 16
        self.sdr_gain = sdr_gain = 30
        self.freq_tx = freq_tx = (fc-150000)
        self.freq_shift = freq_shift = 150000
        self.filter_gain = filter_gain = 210
        self.IQ_bal_phase = IQ_bal_phase = 0
        self.IQ_bal_gain = IQ_bal_gain = 0
        self.DC_offset_Q = DC_offset_Q = 0
        self.DC_offset_I = DC_offset_I = 0

        ##################################################
        # Blocks
        ##################################################

        self._tx_gain_range = qtgui.Range(-23.75, 66, .25, 16, 200)
        self._tx_gain_win = qtgui.RangeWidget(self._tx_gain_range, self.set_tx_gain, "gain_tx", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._tx_gain_win, 0, 0, 1, 2)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._sdr_gain_range = qtgui.Range(0, 50, 1, 30, 200)
        self._sdr_gain_win = qtgui.RangeWidget(self._sdr_gain_range, self.set_sdr_gain, "gain", "counter_slider", int, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._sdr_gain_win, 0, 18, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(18, 19):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._filter_gain_range = qtgui.Range(1, 300, 1, 210, 200)
        self._filter_gain_win = qtgui.RangeWidget(self._filter_gain_range, self.set_filter_gain, "filt_gain", "counter_slider", int, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._filter_gain_win, 0, 2, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._IQ_bal_phase_range = qtgui.Range((-4096), 4096, 1, 0, 200)
        self._IQ_bal_phase_win = qtgui.RangeWidget(self._IQ_bal_phase_range, self.set_IQ_bal_phase, "'IQ_bal_phase'", "counter_slider", int, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._IQ_bal_phase_win, 0, 12, 1, 2)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(12, 14):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._IQ_bal_gain_range = qtgui.Range((-4096), 4096, 1, 0, 200)
        self._IQ_bal_gain_win = qtgui.RangeWidget(self._IQ_bal_gain_range, self.set_IQ_bal_gain, "'IQ_bal_gain'", "counter_slider", int, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._IQ_bal_gain_win, 0, 10, 1, 2)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(10, 12):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._DC_offset_Q_range = qtgui.Range((-2048), 2048, 1, 0, 200)
        self._DC_offset_Q_win = qtgui.RangeWidget(self._DC_offset_Q_range, self.set_DC_offset_Q, "'DC_offset_Q'", "counter_slider", int, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._DC_offset_Q_win, 0, 8, 1, 2)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(8, 10):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._DC_offset_I_range = qtgui.Range((-2048), 2048, 1, 0, 200)
        self._DC_offset_I_win = qtgui.RangeWidget(self._DC_offset_I_range, self.set_DC_offset_I, "'DC_offset_I'", "counter_slider", int, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._DC_offset_I_win, 0, 6, 1, 2)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(6, 8):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.vocoder_gsm_fr_decode_ps_0 = vocoder.gsm_fr_decode_ps()
        self.qtgui_time_sink_x_0 = qtgui.time_sink_c(
            128, #size
            samp_rate, #samp_rate
            "post_scale", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_0.set_update_time(.1)
        self.qtgui_time_sink_x_0.set_y_axis(0, 1)

        self.qtgui_time_sink_x_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0.enable_tags(True)
        self.qtgui_time_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0.enable_autoscale(False)
        self.qtgui_time_sink_x_0.enable_grid(True)
        self.qtgui_time_sink_x_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0.enable_control_panel(True)
        self.qtgui_time_sink_x_0.enable_stem_plot(False)


        labels = ['Max', 'Min', 'Signal 3', 'Signal 4', 'Signal 5',
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
        self.top_layout.addWidget(self._qtgui_time_sink_x_0_win)
        self.qtgui_freq_sink_x_0_0_0 = qtgui.freq_sink_c(
            4096, #size
            window.WIN_HAMMING, #wintype
            0, #fc
            samp_rate, #bw
            "IF", #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_x_0_0_0.set_update_time(0.01)
        self.qtgui_freq_sink_x_0_0_0.set_y_axis((-160), (-30))
        self.qtgui_freq_sink_x_0_0_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0_0_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0_0_0.enable_autoscale(True)
        self.qtgui_freq_sink_x_0_0_0.enable_grid(True)
        self.qtgui_freq_sink_x_0_0_0.set_fft_average(1.0)
        self.qtgui_freq_sink_x_0_0_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0_0_0.enable_control_panel(True)
        self.qtgui_freq_sink_x_0_0_0.set_fft_window_normalized(False)



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
                self.qtgui_freq_sink_x_0_0_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0_0_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0_0_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0_0_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0_0_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_0_0_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_0_0_0.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_freq_sink_x_0_0_0_win, 1, 12, 1, 6)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(12, 18):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_freq_sink_x_0_0 = qtgui.freq_sink_c(
            1024, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate, #bw
            "1", #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_x_0_0.set_update_time(0.10)
        self.qtgui_freq_sink_x_0_0.set_y_axis((-140), 10)
        self.qtgui_freq_sink_x_0_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_0_0.enable_grid(False)
        self.qtgui_freq_sink_x_0_0.set_fft_average(0.1)
        self.qtgui_freq_sink_x_0_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0_0.enable_control_panel(True)
        self.qtgui_freq_sink_x_0_0.set_fft_window_normalized(False)



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
                self.qtgui_freq_sink_x_0_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_0_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_0_0.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_freq_sink_x_0_0_win, 1, 6, 1, 6)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(6, 12):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_freq_sink_x_0 = qtgui.freq_sink_c(
            1024, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate, #bw
            "", #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_x_0.set_update_time(0.10)
        self.qtgui_freq_sink_x_0.set_y_axis((-140), 10)
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
        self.top_grid_layout.addWidget(self._qtgui_freq_sink_x_0_win, 1, 0, 1, 6)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 6):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.pdu_pdu_to_tagged_stream_0 = pdu.pdu_to_tagged_stream(gr.types.byte_t, 'packet_len')
        self.network_socket_pdu_1 = network.socket_pdu('UDP_SERVER', '127.0.0.1', '4729', 10000, False)
        self.network_socket_pdu_0 = network.socket_pdu('UDP_CLIENT', '127.0.0.1', '4729', 10000, False)
        self.gsm_tch_f_decoder_0 = gsm.tch_f_decoder(gsm.TCH_FS, True)
        self.gsm_tch_f_chans_demapper_0 = gsm.tch_f_chans_demapper(5)
        self.gsm_receiver_0 = gsm.receiver(osr, [0], [], False)
        self.gsm_message_printer_0_1 = gsm.message_printer(pmt.intern(""), False,
            False, False)
        self.gsm_message_printer_0 = gsm.message_printer(pmt.intern(""), False,
            False, False)
        self.gsm_input_0 = gsm.gsm_input(
            ppm=0,
            osr=osr,
            fc=fc,
            samp_rate_in=samp_rate,
        )
        self.gsm_decryption_0_0_0_0 = gsm.decryption([0x1e, 0xf0, 0x0b, 0xab, 0x3b, 0xac, 0x70, 0x02], 1)
        self.gsm_decryption_0_0_0 = gsm.decryption([0x1e, 0xf0, 0x0b, 0xab, 0x3b, 0xac, 0x70, 0x02], 1)
        self.gsm_control_channels_decoder_0 = gsm.control_channels_decoder()
        self.gsm_clock_offset_control_0 = gsm.clock_offset_control(fc, samp_rate, osr)
        self.freq_xlating_fir_filter_xxx_0 = filter.freq_xlating_fir_filter_ccc(1, firdes.low_pass(filter_gain,samp_rate,samp_rate/2, 100e3), 0, samp_rate)
        self._freq_tx_tool_bar = Qt.QToolBar(self)
        self._freq_tx_tool_bar.addWidget(Qt.QLabel("Frequency tx" + ": "))
        self._freq_tx_line_edit = Qt.QLineEdit(str(self.freq_tx))
        self._freq_tx_tool_bar.addWidget(self._freq_tx_line_edit)
        self._freq_tx_line_edit.editingFinished.connect(
            lambda: self.set_freq_tx(eng_notation.str_to_num(str(self._freq_tx_line_edit.text()))))
        self.top_grid_layout.addWidget(self._freq_tx_tool_bar, 0, 3, 1, 2)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(3, 5):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._freq_shift_range = qtgui.Range(-samp_rate/2, samp_rate/2, 1, 150000, 200)
        self._freq_shift_win = qtgui.RangeWidget(self._freq_shift_range, self.set_freq_shift, "freq shift", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._freq_shift_win, 0, 5, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(5, 6):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.blocks_throttle2_1 = blocks.throttle( gr.sizeof_gr_complex*1, samp_rate, True, 0 if "auto" == "auto" else max( int(float(0.1) * samp_rate) if "auto" == "time" else int(0.1), 1) )
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_char*1, 33)
        self.blocks_short_to_float_0 = blocks.short_to_float(1, 32767.0)
        self.blocks_interleaved_short_to_complex_0_0 = blocks.interleaved_short_to_complex(False, False,2047.0)
        self.blocks_interleaved_short_to_complex_0 = blocks.interleaved_short_to_complex(False, False,2047)
        self.blocks_file_source_0 = blocks.file_source(gr.sizeof_gr_complex*1, '/home/subrad/work/gsm_work/gr-gsm/test_data/vf_call6_a725_d174_g5_Kc1EF00BAB3BAC7002.cfile', True, 0, 0)
        self.blocks_file_source_0.set_begin_tag(pmt.PMT_NIL)
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_char*1, 'out.gsm', False)
        self.blocks_file_sink_0.set_unbuffered(False)
        self.blocks_complex_to_interleaved_short_0 = blocks.complex_to_interleaved_short(False,2047.0)
        self.blocks_abs_xx_0_0 = blocks.abs_ss(1)
        self.bladeRF_source_0 = bladeRF.source(
            args="numchan=" + str(1)
                 + ",metadata=" + 'False'
                 + ",bladerf=" +  str('ae900f3814034d5f9d219f2244937943')
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
        self.bladeRF_source_0.set_sample_rate(samp_rate)
        self.bladeRF_source_0.set_center_freq(fc,0)
        self.bladeRF_source_0.set_bandwidth(samp_rate,0)
        self.bladeRF_source_0.set_dc_offset_mode(0, 0)
        self.bladeRF_source_0.set_iq_balance_mode(0, 0)
        self.bladeRF_source_0.set_gain_mode(False, 0)
        self.bladeRF_source_0.set_gain(sdr_gain, 0)
        self.bladeRF_source_0.set_if_gain(sdr_gain, 0)
        self.bladeRF_sink_0 = bladeRF.sink(
            args="numchan=" + str(1)
                 + ",metadata=" + 'False'
                 + ",bladerf=" +  str('c4af21dcdf8547d79fa1e9e475082cd3')
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
        self.bladeRF_sink_0.set_sample_rate(samp_rate)
        self.bladeRF_sink_0.set_center_freq(fc,0)
        self.bladeRF_sink_0.set_bandwidth(samp_rate,0)
        self.bladeRF_sink_0.set_gain(tx_gain, 0)
        self.bladeRF_sink_0.set_if_gain(tx_gain, 0)
        self.bladeRF_sink_0.set_dc_offset(
            complex(DC_offset_I, DC_offset_Q),
            0
        )
        self.bladeRF_sink_0.set_iq_balance(
            complex(IQ_bal_gain, IQ_bal_phase),
            0
        )
        self.audio_sink_0 = audio.sink(8000, '', True)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.gsm_clock_offset_control_0, 'ctrl'), (self.gsm_input_0, 'ctrl_in'))
        self.msg_connect((self.gsm_control_channels_decoder_0, 'msgs'), (self.gsm_message_printer_0, 'msgs'))
        self.msg_connect((self.gsm_control_channels_decoder_0, 'msgs'), (self.network_socket_pdu_0, 'pdus'))
        self.msg_connect((self.gsm_decryption_0_0_0, 'bursts'), (self.gsm_tch_f_decoder_0, 'bursts'))
        self.msg_connect((self.gsm_decryption_0_0_0_0, 'bursts'), (self.gsm_control_channels_decoder_0, 'bursts'))
        self.msg_connect((self.gsm_receiver_0, 'measurements'), (self.gsm_clock_offset_control_0, 'measurements'))
        self.msg_connect((self.gsm_receiver_0, 'C0'), (self.gsm_tch_f_chans_demapper_0, 'bursts'))
        self.msg_connect((self.gsm_tch_f_chans_demapper_0, 'tch_bursts'), (self.gsm_decryption_0_0_0, 'bursts'))
        self.msg_connect((self.gsm_tch_f_chans_demapper_0, 'acch_bursts'), (self.gsm_decryption_0_0_0_0, 'bursts'))
        self.msg_connect((self.gsm_tch_f_decoder_0, 'msgs'), (self.gsm_message_printer_0_1, 'msgs'))
        self.msg_connect((self.gsm_tch_f_decoder_0, 'msgs'), (self.network_socket_pdu_0, 'pdus'))
        self.msg_connect((self.gsm_tch_f_decoder_0, 'voice'), (self.pdu_pdu_to_tagged_stream_0, 'pdus'))
        self.connect((self.bladeRF_source_0, 0), (self.gsm_input_0, 0))
        self.connect((self.bladeRF_source_0, 0), (self.qtgui_freq_sink_x_0, 0))
        self.connect((self.blocks_abs_xx_0_0, 0), (self.blocks_interleaved_short_to_complex_0, 0))
        self.connect((self.blocks_complex_to_interleaved_short_0, 0), (self.blocks_abs_xx_0_0, 0))
        self.connect((self.blocks_complex_to_interleaved_short_0, 0), (self.blocks_interleaved_short_to_complex_0_0, 0))
        self.connect((self.blocks_file_source_0, 0), (self.blocks_throttle2_1, 0))
        self.connect((self.blocks_interleaved_short_to_complex_0, 0), (self.qtgui_time_sink_x_0, 0))
        self.connect((self.blocks_interleaved_short_to_complex_0_0, 0), (self.bladeRF_sink_0, 0))
        self.connect((self.blocks_interleaved_short_to_complex_0_0, 0), (self.qtgui_freq_sink_x_0_0_0, 0))
        self.connect((self.blocks_short_to_float_0, 0), (self.audio_sink_0, 0))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.vocoder_gsm_fr_decode_ps_0, 0))
        self.connect((self.blocks_throttle2_1, 0), (self.freq_xlating_fir_filter_xxx_0, 0))
        self.connect((self.blocks_throttle2_1, 0), (self.qtgui_freq_sink_x_0_0, 0))
        self.connect((self.freq_xlating_fir_filter_xxx_0, 0), (self.blocks_complex_to_interleaved_short_0, 0))
        self.connect((self.gsm_input_0, 0), (self.gsm_receiver_0, 0))
        self.connect((self.pdu_pdu_to_tagged_stream_0, 0), (self.blocks_file_sink_0, 0))
        self.connect((self.pdu_pdu_to_tagged_stream_0, 0), (self.blocks_stream_to_vector_0, 0))
        self.connect((self.vocoder_gsm_fr_decode_ps_0, 0), (self.blocks_short_to_float_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "tch_f_reception")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_fc(self):
        return self.fc

    def set_fc(self, fc):
        self.fc = fc
        self.set_freq_tx((self.fc-150000))
        self.bladeRF_sink_0.set_center_freq(self.fc, 0)
        self.bladeRF_source_0.set_center_freq(self.fc, 0)
        self.gsm_clock_offset_control_0.set_fc(self.fc)
        self.gsm_input_0.set_fc(self.fc)

    def get_osr(self):
        return self.osr

    def set_osr(self, osr):
        self.osr = osr
        self.gsm_input_0.set_osr(self.osr)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.bladeRF_sink_0.set_sample_rate(self.samp_rate)
        self.bladeRF_sink_0.set_bandwidth(self.samp_rate, 0)
        self.bladeRF_source_0.set_sample_rate(self.samp_rate)
        self.bladeRF_source_0.set_bandwidth(self.samp_rate, 0)
        self.blocks_throttle2_1.set_sample_rate(self.samp_rate)
        self.freq_xlating_fir_filter_xxx_0.set_taps(firdes.low_pass(self.filter_gain,self.samp_rate,self.samp_rate/2, 100e3))
        self.gsm_input_0.set_samp_rate_in(self.samp_rate)
        self.qtgui_freq_sink_x_0.set_frequency_range(0, self.samp_rate)
        self.qtgui_freq_sink_x_0_0.set_frequency_range(0, self.samp_rate)
        self.qtgui_freq_sink_x_0_0_0.set_frequency_range(0, self.samp_rate)
        self.qtgui_time_sink_x_0.set_samp_rate(self.samp_rate)

    def get_tx_gain(self):
        return self.tx_gain

    def set_tx_gain(self, tx_gain):
        self.tx_gain = tx_gain
        self.bladeRF_sink_0.set_gain(self.tx_gain, 0)
        self.bladeRF_sink_0.set_if_gain(self.tx_gain, 0)

    def get_sdr_gain(self):
        return self.sdr_gain

    def set_sdr_gain(self, sdr_gain):
        self.sdr_gain = sdr_gain
        self.bladeRF_source_0.set_gain(self.sdr_gain, 0)
        self.bladeRF_source_0.set_if_gain(self.sdr_gain, 0)

    def get_freq_tx(self):
        return self.freq_tx

    def set_freq_tx(self, freq_tx):
        self.freq_tx = freq_tx
        Qt.QMetaObject.invokeMethod(self._freq_tx_line_edit, "setText", Qt.Q_ARG("QString", eng_notation.num_to_str(self.freq_tx)))

    def get_freq_shift(self):
        return self.freq_shift

    def set_freq_shift(self, freq_shift):
        self.freq_shift = freq_shift

    def get_filter_gain(self):
        return self.filter_gain

    def set_filter_gain(self, filter_gain):
        self.filter_gain = filter_gain
        self.freq_xlating_fir_filter_xxx_0.set_taps(firdes.low_pass(self.filter_gain,self.samp_rate,self.samp_rate/2, 100e3))

    def get_IQ_bal_phase(self):
        return self.IQ_bal_phase

    def set_IQ_bal_phase(self, IQ_bal_phase):
        self.IQ_bal_phase = IQ_bal_phase
        self.bladeRF_sink_0.set_iq_balance(complex(self.IQ_bal_gain, self.IQ_bal_phase), 0)

    def get_IQ_bal_gain(self):
        return self.IQ_bal_gain

    def set_IQ_bal_gain(self, IQ_bal_gain):
        self.IQ_bal_gain = IQ_bal_gain
        self.bladeRF_sink_0.set_iq_balance(complex(self.IQ_bal_gain, self.IQ_bal_phase), 0)

    def get_DC_offset_Q(self):
        return self.DC_offset_Q

    def set_DC_offset_Q(self, DC_offset_Q):
        self.DC_offset_Q = DC_offset_Q
        self.bladeRF_sink_0.set_dc_offset(complex(self.DC_offset_I, self.DC_offset_Q), 0)

    def get_DC_offset_I(self):
        return self.DC_offset_I

    def set_DC_offset_I(self, DC_offset_I):
        self.DC_offset_I = DC_offset_I
        self.bladeRF_sink_0.set_dc_offset(complex(self.DC_offset_I, self.DC_offset_Q), 0)



def argument_parser():
    parser = ArgumentParser()
    parser.add_argument(
        "-f", "--fc", dest="fc", type=eng_float, default=eng_notation.num_to_str(float(937e6)),
        help="Set fc [default=%(default)r]")
    parser.add_argument(
        "--osr", dest="osr", type=intx, default=4,
        help="Set OSR [default=%(default)r]")
    parser.add_argument(
        "-s", "--samp-rate", dest="samp_rate", type=eng_float, default=eng_notation.num_to_str(float((100.0e6/174.0))),
        help="Set samp_rate [default=%(default)r]")
    return parser


def main(top_block_cls=tch_f_reception, options=None):
    if options is None:
        options = argument_parser().parse_args()

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls(fc=options.fc, osr=options.osr, samp_rate=options.samp_rate)

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
