#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Scale cfile to 12bit
# Author: Bradley C.
# Description: Use this function to read in a cfile IQ file and scale it for bladeRF 12bit. Hit write sigmf checkbox to lock in data
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5 import QtCore
from gnuradio import blocks
import numpy as np
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
import sip
import threading



class scale_gsm_for_12bit(gr.top_block, Qt.QWidget):

    def __init__(self, fc=910e6, input_file_name='../test_data/sms_multirtl_downlink_tail.cfile', output_file_name='../test_data/gsm_downlink_BCCH_tail', samp_rate_in=1e6):
        gr.top_block.__init__(self, "Scale cfile to 12bit", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Scale cfile to 12bit")
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

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "scale_gsm_for_12bit")

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
        self.output_file_name = output_file_name
        self.samp_rate_in = samp_rate_in

        ##################################################
        # Variables
        ##################################################
        self.sample_rate_switch = sample_rate_switch = samp_rate_in
        self.os = os = __import__('os')
        self.input_cfile_entry = input_cfile_entry = input_file_name
        self.write_to_sigmf = write_to_sigmf = 0
        self.variable_qtgui_entry_0 = variable_qtgui_entry_0 = sample_rate_switch
        self.output_sigmf_entry = output_sigmf_entry = output_file_name
        self.n_iq = n_iq = int(os.path.getsize(input_cfile_entry) // gr.sizeof_gr_complex)*2
        self.gsm_sample_rate = gsm_sample_rate = (270.8334e3 + 8e3)/2
        self.filter_gain = filter_gain = 29
        self.bcc_tch_filter = bcc_tch_filter = 0

        ##################################################
        # Blocks
        ##################################################

        _write_to_sigmf_check_box = Qt.QCheckBox("Write to Sigmf")
        self._write_to_sigmf_choices = {True: 1, False: 0}
        self._write_to_sigmf_choices_inv = dict((v,k) for k,v in self._write_to_sigmf_choices.items())
        self._write_to_sigmf_callback = lambda i: Qt.QMetaObject.invokeMethod(_write_to_sigmf_check_box, "setChecked", Qt.Q_ARG("bool", self._write_to_sigmf_choices_inv[i]))
        self._write_to_sigmf_callback(self.write_to_sigmf)
        _write_to_sigmf_check_box.stateChanged.connect(lambda i: self.set_write_to_sigmf(self._write_to_sigmf_choices[bool(i)]))
        self.top_grid_layout.addWidget(_write_to_sigmf_check_box, 1, 0, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._sample_rate_switch_choices = {'Pressed': (100.0e6/174), 'Released': 1e6}

        _sample_rate_switch_toggle_switch = qtgui.GrToggleSwitch(self.set_sample_rate_switch, 'BCCH/TCH Fs', self._sample_rate_switch_choices, False, "green", "gray", 4, 50, 1, 1, self, 'pmt.to_pmt(True)')
        self.sample_rate_switch = _sample_rate_switch_toggle_switch

        self.top_grid_layout.addWidget(_sample_rate_switch_toggle_switch, 1, 2, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._output_sigmf_entry_tool_bar = Qt.QToolBar(self)
        self._output_sigmf_entry_tool_bar.addWidget(Qt.QLabel("SigMf Data outpath" + ": "))
        self._output_sigmf_entry_line_edit = Qt.QLineEdit(str(self.output_sigmf_entry))
        self._output_sigmf_entry_tool_bar.addWidget(self._output_sigmf_entry_line_edit)
        self._output_sigmf_entry_line_edit.editingFinished.connect(
            lambda: self.set_output_sigmf_entry(str(str(self._output_sigmf_entry_line_edit.text()))))
        self.top_grid_layout.addWidget(self._output_sigmf_entry_tool_bar, 0, 2, 1, 2)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 4):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._input_cfile_entry_tool_bar = Qt.QToolBar(self)
        self._input_cfile_entry_tool_bar.addWidget(Qt.QLabel("Cfile Data filepath" + ": "))
        self._input_cfile_entry_line_edit = Qt.QLineEdit(str(self.input_cfile_entry))
        self._input_cfile_entry_tool_bar.addWidget(self._input_cfile_entry_line_edit)
        self._input_cfile_entry_line_edit.editingFinished.connect(
            lambda: self.set_input_cfile_entry(str(str(self._input_cfile_entry_line_edit.text()))))
        self.top_grid_layout.addWidget(self._input_cfile_entry_tool_bar, 0, 0, 1, 2)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._filter_gain_range = qtgui.Range(1, 300, 1, 29, 200)
        self._filter_gain_win = qtgui.RangeWidget(self._filter_gain_range, self.set_filter_gain, "filt_gain", "counter_slider", int, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._filter_gain_win, 2, 0, 1, 2)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        _bcc_tch_filter_check_box = Qt.QCheckBox("Channel Filter (BCCH/TCH) Select")
        self._bcc_tch_filter_choices = {True: 1, False: 0}
        self._bcc_tch_filter_choices_inv = dict((v,k) for k,v in self._bcc_tch_filter_choices.items())
        self._bcc_tch_filter_callback = lambda i: Qt.QMetaObject.invokeMethod(_bcc_tch_filter_check_box, "setChecked", Qt.Q_ARG("bool", self._bcc_tch_filter_choices_inv[i]))
        self._bcc_tch_filter_callback(self.bcc_tch_filter)
        _bcc_tch_filter_check_box.stateChanged.connect(lambda i: self.set_bcc_tch_filter(self._bcc_tch_filter_choices[bool(i)]))
        self.top_grid_layout.addWidget(_bcc_tch_filter_check_box, 2, 2, 1, 1)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._variable_qtgui_entry_0_tool_bar = Qt.QToolBar(self)
        self._variable_qtgui_entry_0_tool_bar.addWidget(Qt.QLabel("sample rate" + ": "))
        self._variable_qtgui_entry_0_line_edit = Qt.QLineEdit(str(self.variable_qtgui_entry_0))
        self._variable_qtgui_entry_0_tool_bar.addWidget(self._variable_qtgui_entry_0_line_edit)
        self._variable_qtgui_entry_0_line_edit.returnPressed.connect(
            lambda: self.set_variable_qtgui_entry_0(eng_notation.str_to_num(str(self._variable_qtgui_entry_0_line_edit.text()))))
        self.top_grid_layout.addWidget(self._variable_qtgui_entry_0_tool_bar, 1, 1, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_time_sink_x_0 = qtgui.time_sink_c(
            (4096*64), #size
            sample_rate_switch, #samp_rate
            'Max IQ value SigMF (scaled by 2048)', #name
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
        self.top_grid_layout.addWidget(self._qtgui_time_sink_x_0_win, 3, 2, 2, 2)
        for r in range(3, 5):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 4):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_freq_sink_x_0_0_0 = qtgui.freq_sink_c(
            4096, #size
            window.WIN_HAMMING, #wintype
            0, #fc
            sample_rate_switch, #bw
            "SigMF Output PSD", #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_x_0_0_0.set_update_time(0.01)
        self.qtgui_freq_sink_x_0_0_0.set_y_axis((-140), (-0))
        self.qtgui_freq_sink_x_0_0_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0_0_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0_0_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_0_0_0.enable_grid(True)
        self.qtgui_freq_sink_x_0_0_0.set_fft_average(0.2)
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
        self.top_grid_layout.addWidget(self._qtgui_freq_sink_x_0_0_0_win, 3, 0, 2, 2)
        for r in range(3, 5):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_freq_sink_x_0_0 = qtgui.freq_sink_c(
            1024, #size
            window.WIN_HANN, #wintype
            0, #fc
            sample_rate_switch, #bw
            "Cfile Input PSD", #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_x_0_0.set_update_time(0.10)
        self.qtgui_freq_sink_x_0_0.set_y_axis((-100), (-40))
        self.qtgui_freq_sink_x_0_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_0_0.enable_grid(True)
        self.qtgui_freq_sink_x_0_0.set_fft_average(1.0)
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
        self.top_grid_layout.addWidget(self._qtgui_freq_sink_x_0_0_win, 0, 4, 2, 2)
        for r in range(0, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(4, 6):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.freq_xlating_fir_filter_xxx_0_0_0 = filter.freq_xlating_fir_filter_ccc(1, firdes.low_pass(filter_gain,100e6/174, 190e3, 20e3), 0, (100e6/174))
        self.freq_xlating_fir_filter_xxx_0 = filter.freq_xlating_fir_filter_ccc(1, firdes.low_pass(filter_gain,1e6,gsm_sample_rate,gsm_sample_rate*.2), .0, 1e6)
        self.blocks_throttle2_0 = blocks.throttle( gr.sizeof_gr_complex*1, sample_rate_switch, True, 0 if "auto" == "auto" else max( int(float(0.1) * sample_rate_switch) if "auto" == "time" else int(0.1), 1) )
        self.blocks_sigmf_sink_minimal_0 = blocks.sigmf_sink_minimal(
            item_size=gr.sizeof_short,
            filename=output_sigmf_entry,
            sample_rate=sample_rate_switch,
            center_freq=fc,
            author='',
            description='Signal should be centered around TX Freq. Signal BW ~= 280kHz Generated using sms_multirtl_downlink_tail.cfile scaled to 12bit. ',
            hw_info='',
            is_complex=True)
        self.blocks_selector_0_0 = blocks.selector(gr.sizeof_gr_complex*1,bcc_tch_filter,0)
        self.blocks_selector_0_0.set_enabled(True)
        self.blocks_selector_0 = blocks.selector(gr.sizeof_short*1,0,write_to_sigmf)
        self.blocks_selector_0.set_enabled(True)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_short*1)
        self.blocks_interleaved_short_to_complex_0_0 = blocks.interleaved_short_to_complex(False, False,2047.0)
        self.blocks_interleaved_short_to_complex_0 = blocks.interleaved_short_to_complex(False, False,2047)
        self.blocks_head_0 = blocks.head(gr.sizeof_short*1, n_iq)
        self.blocks_file_source_0 = blocks.file_source(gr.sizeof_gr_complex*1, input_cfile_entry, True, 0, 0)
        self.blocks_file_source_0.set_begin_tag(pmt.intern("file_begin"))
        self.blocks_complex_to_interleaved_short_0 = blocks.complex_to_interleaved_short(False,2047.0)
        self.blocks_abs_xx_0_0 = blocks.abs_ss(1)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_abs_xx_0_0, 0), (self.blocks_interleaved_short_to_complex_0, 0))
        self.connect((self.blocks_complex_to_interleaved_short_0, 0), (self.blocks_abs_xx_0_0, 0))
        self.connect((self.blocks_complex_to_interleaved_short_0, 0), (self.blocks_interleaved_short_to_complex_0_0, 0))
        self.connect((self.blocks_complex_to_interleaved_short_0, 0), (self.blocks_selector_0, 0))
        self.connect((self.blocks_file_source_0, 0), (self.blocks_throttle2_0, 0))
        self.connect((self.blocks_head_0, 0), (self.blocks_sigmf_sink_minimal_0, 0))
        self.connect((self.blocks_interleaved_short_to_complex_0, 0), (self.qtgui_time_sink_x_0, 0))
        self.connect((self.blocks_interleaved_short_to_complex_0_0, 0), (self.qtgui_freq_sink_x_0_0_0, 0))
        self.connect((self.blocks_selector_0, 1), (self.blocks_head_0, 0))
        self.connect((self.blocks_selector_0, 0), (self.blocks_null_sink_0, 0))
        self.connect((self.blocks_selector_0_0, 0), (self.blocks_complex_to_interleaved_short_0, 0))
        self.connect((self.blocks_throttle2_0, 0), (self.freq_xlating_fir_filter_xxx_0, 0))
        self.connect((self.blocks_throttle2_0, 0), (self.freq_xlating_fir_filter_xxx_0_0_0, 0))
        self.connect((self.blocks_throttle2_0, 0), (self.qtgui_freq_sink_x_0_0, 0))
        self.connect((self.freq_xlating_fir_filter_xxx_0, 0), (self.blocks_selector_0_0, 0))
        self.connect((self.freq_xlating_fir_filter_xxx_0_0_0, 0), (self.blocks_selector_0_0, 1))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "scale_gsm_for_12bit")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_fc(self):
        return self.fc

    def set_fc(self, fc):
        self.fc = fc

    def get_input_file_name(self):
        return self.input_file_name

    def set_input_file_name(self, input_file_name):
        self.input_file_name = input_file_name
        self.set_input_cfile_entry(self.input_file_name)

    def get_output_file_name(self):
        return self.output_file_name

    def set_output_file_name(self, output_file_name):
        self.output_file_name = output_file_name
        self.set_output_sigmf_entry(self.output_file_name)

    def get_samp_rate_in(self):
        return self.samp_rate_in

    def set_samp_rate_in(self, samp_rate_in):
        self.samp_rate_in = samp_rate_in

    def get_sample_rate_switch(self):
        return self.sample_rate_switch

    def set_sample_rate_switch(self, sample_rate_switch):
        self.sample_rate_switch = sample_rate_switch
        self.set_variable_qtgui_entry_0(self.sample_rate_switch)
        self.blocks_throttle2_0.set_sample_rate(self.sample_rate_switch)
        self.qtgui_freq_sink_x_0_0.set_frequency_range(0, self.sample_rate_switch)
        self.qtgui_freq_sink_x_0_0_0.set_frequency_range(0, self.sample_rate_switch)
        self.qtgui_time_sink_x_0.set_samp_rate(self.sample_rate_switch)

    def get_os(self):
        return self.os

    def set_os(self, os):
        self.os = os

    def get_input_cfile_entry(self):
        return self.input_cfile_entry

    def set_input_cfile_entry(self, input_cfile_entry):
        self.input_cfile_entry = input_cfile_entry
        Qt.QMetaObject.invokeMethod(self._input_cfile_entry_line_edit, "setText", Qt.Q_ARG("QString", str(self.input_cfile_entry)))
        self.set_n_iq(int(os.path.getsize(self.input_cfile_entry) // gr.sizeof_gr_complex)*2)
        self.blocks_file_source_0.open(self.input_cfile_entry, True)

    def get_write_to_sigmf(self):
        return self.write_to_sigmf

    def set_write_to_sigmf(self, write_to_sigmf):
        self.write_to_sigmf = write_to_sigmf
        self._write_to_sigmf_callback(self.write_to_sigmf)
        self.blocks_selector_0.set_output_index(self.write_to_sigmf)

    def get_variable_qtgui_entry_0(self):
        return self.variable_qtgui_entry_0

    def set_variable_qtgui_entry_0(self, variable_qtgui_entry_0):
        self.variable_qtgui_entry_0 = variable_qtgui_entry_0
        Qt.QMetaObject.invokeMethod(self._variable_qtgui_entry_0_line_edit, "setText", Qt.Q_ARG("QString", eng_notation.num_to_str(self.variable_qtgui_entry_0)))

    def get_output_sigmf_entry(self):
        return self.output_sigmf_entry

    def set_output_sigmf_entry(self, output_sigmf_entry):
        self.output_sigmf_entry = output_sigmf_entry
        Qt.QMetaObject.invokeMethod(self._output_sigmf_entry_line_edit, "setText", Qt.Q_ARG("QString", str(self.output_sigmf_entry)))

    def get_n_iq(self):
        return self.n_iq

    def set_n_iq(self, n_iq):
        self.n_iq = n_iq
        self.blocks_head_0.set_length(self.n_iq)

    def get_gsm_sample_rate(self):
        return self.gsm_sample_rate

    def set_gsm_sample_rate(self, gsm_sample_rate):
        self.gsm_sample_rate = gsm_sample_rate
        self.freq_xlating_fir_filter_xxx_0.set_taps(firdes.low_pass(self.filter_gain,1e6,self.gsm_sample_rate,self.gsm_sample_rate*.2))

    def get_filter_gain(self):
        return self.filter_gain

    def set_filter_gain(self, filter_gain):
        self.filter_gain = filter_gain
        self.freq_xlating_fir_filter_xxx_0.set_taps(firdes.low_pass(self.filter_gain,1e6,self.gsm_sample_rate,self.gsm_sample_rate*.2))
        self.freq_xlating_fir_filter_xxx_0_0_0.set_taps(firdes.low_pass(self.filter_gain,100e6/174, 190e3, 20e3))

    def get_bcc_tch_filter(self):
        return self.bcc_tch_filter

    def set_bcc_tch_filter(self, bcc_tch_filter):
        self.bcc_tch_filter = bcc_tch_filter
        self._bcc_tch_filter_callback(self.bcc_tch_filter)
        self.blocks_selector_0_0.set_input_index(self.bcc_tch_filter)



def argument_parser():
    description = 'Use this function to read in a cfile IQ file and scale it for bladeRF 12bit. Hit write sigmf checkbox to lock in data'
    parser = ArgumentParser(description=description)
    parser.add_argument(
        "--fc", dest="fc", type=eng_float, default=eng_notation.num_to_str(float(910e6)),
        help="Set fc [default=%(default)r]")
    parser.add_argument(
        "-i", "--input-file-name", dest="input_file_name", type=str, default='../test_data/sms_multirtl_downlink_tail.cfile',
        help="Set input_file_name [default=%(default)r]")
    parser.add_argument(
        "-o", "--output-file-name", dest="output_file_name", type=str, default='../test_data/gsm_downlink_BCCH_tail',
        help="Set output_file_name [default=%(default)r]")
    parser.add_argument(
        "--samp-rate-in", dest="samp_rate_in", type=eng_float, default=eng_notation.num_to_str(float(1e6)),
        help="Set fs [default=%(default)r]")
    return parser


def main(top_block_cls=scale_gsm_for_12bit, options=None):
    if options is None:
        options = argument_parser().parse_args()

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls(fc=options.fc, input_file_name=options.input_file_name, output_file_name=options.output_file_name, samp_rate_in=options.samp_rate_in)

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
