#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: GSM TCH Transmitter bladeRF/SigMF
# Author: Bradley C
# Description: Default to TCH filepath with test data Fs
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5 import QtCore
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
import bladeRF
import time
import sip
import threading



class transmit_tch_bladerf(gr.top_block, Qt.QWidget):

    def __init__(self, fc=937e6, input_file_name='../test_data/gsm_test_voice_call.sigmf-data', samp_rate=(100e6/174), serial_id="", tx_gain_in=16):
        gr.top_block.__init__(self, "GSM TCH Transmitter bladeRF/SigMF ", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("GSM TCH Transmitter bladeRF/SigMF ")
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

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "transmit_tch_bladerf")

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
        self.samp_rate = samp_rate
        self.serial_id = serial_id
        self.tx_gain_in = tx_gain_in

        ##################################################
        # Variables
        ##################################################
        self.tx_gain = tx_gain = tx_gain_in
        self.input_sigmf_entry = input_sigmf_entry = input_file_name
        self.freq_tx = freq_tx = fc

        ##################################################
        # Blocks
        ##################################################

        self._tx_gain_range = qtgui.Range(-23.75, 66, .25, tx_gain_in, 200)
        self._tx_gain_win = qtgui.RangeWidget(self._tx_gain_range, self.set_tx_gain, "'tx_gain'", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._tx_gain_win, 1, 3, 1, 3)
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
        self._freq_tx_tool_bar = Qt.QToolBar(self)
        self._freq_tx_tool_bar.addWidget(Qt.QLabel("Frequency tx" + ": "))
        self._freq_tx_line_edit = Qt.QLineEdit(str(self.freq_tx))
        self._freq_tx_tool_bar.addWidget(self._freq_tx_line_edit)
        self._freq_tx_line_edit.editingFinished.connect(
            lambda: self.set_freq_tx(eng_notation.str_to_num(str(self._freq_tx_line_edit.text()))))
        self.top_grid_layout.addWidget(self._freq_tx_tool_bar, 1, 0, 1, 3)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_time_sink_x_0 = qtgui.time_sink_c(
            (4096*64), #size
            samp_rate, #samp_rate
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
        self.top_grid_layout.addWidget(self._qtgui_time_sink_x_0_win, 9, 0, 1, 6)
        for r in range(9, 10):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 6):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_freq_sink_x_0_0 = qtgui.freq_sink_c(
            2048, #size
            window.WIN_HANN, #wintype
            0, #fc
            samp_rate, #bw
            "Freq Domain of SigMF", #name
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
        self.top_grid_layout.addWidget(self._qtgui_freq_sink_x_0_0_win, 2, 0, 1, 6)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 6):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.blocks_throttle2_0 = blocks.throttle( gr.sizeof_gr_complex*1, samp_rate, True, 0 if "auto" == "auto" else max( int(float(0.1) * samp_rate) if "auto" == "time" else int(0.1), 1) )
        self.blocks_sigmf_source_minimal_0 = blocks.file_source(gr.sizeof_short, input_sigmf_entry, True, 0, 0)
        self.blocks_sigmf_source_minimal_0.set_begin_tag(pmt.PMT_NIL)
        self.blocks_interleaved_short_to_complex_0_0_0 = blocks.interleaved_short_to_complex(False, False,2047.0)
        self.blocks_interleaved_short_to_complex_0 = blocks.interleaved_short_to_complex(False, False,2047)
        self.blocks_abs_xx_0_0 = blocks.abs_ss(1)
        self.bladeRF_sink_0 = bladeRF.sink(
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
                 + ",bias_tee0="+'True'
                 + ",bias_tee1="+'False'


        )
        self.bladeRF_sink_0.set_sample_rate(samp_rate)
        self.bladeRF_sink_0.set_center_freq(freq_tx,0)
        self.bladeRF_sink_0.set_bandwidth(samp_rate,0)
        self.bladeRF_sink_0.set_gain(tx_gain, 0)
        self.bladeRF_sink_0.set_if_gain(tx_gain, 0)
        self.bladeRF_sink_0.set_dc_offset(
            complex(0, 0),
            0
        )
        self.bladeRF_sink_0.set_iq_balance(
            complex(0, 0),
            0
        )


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_abs_xx_0_0, 0), (self.blocks_interleaved_short_to_complex_0, 0))
        self.connect((self.blocks_interleaved_short_to_complex_0, 0), (self.qtgui_time_sink_x_0, 0))
        self.connect((self.blocks_interleaved_short_to_complex_0_0_0, 0), (self.blocks_throttle2_0, 0))
        self.connect((self.blocks_sigmf_source_minimal_0, 0), (self.blocks_abs_xx_0_0, 0))
        self.connect((self.blocks_sigmf_source_minimal_0, 0), (self.blocks_interleaved_short_to_complex_0_0_0, 0))
        self.connect((self.blocks_throttle2_0, 0), (self.bladeRF_sink_0, 0))
        self.connect((self.blocks_throttle2_0, 0), (self.qtgui_freq_sink_x_0_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "transmit_tch_bladerf")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_fc(self):
        return self.fc

    def set_fc(self, fc):
        self.fc = fc
        self.set_freq_tx(self.fc)

    def get_input_file_name(self):
        return self.input_file_name

    def set_input_file_name(self, input_file_name):
        self.input_file_name = input_file_name
        self.set_input_sigmf_entry(self.input_file_name)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.bladeRF_sink_0.set_sample_rate(self.samp_rate)
        self.bladeRF_sink_0.set_bandwidth(self.samp_rate, 0)
        self.blocks_throttle2_0.set_sample_rate(self.samp_rate)
        self.qtgui_freq_sink_x_0_0.set_frequency_range(0, self.samp_rate)
        self.qtgui_time_sink_x_0.set_samp_rate(self.samp_rate)

    def get_serial_id(self):
        return self.serial_id

    def set_serial_id(self, serial_id):
        self.serial_id = serial_id

    def get_tx_gain_in(self):
        return self.tx_gain_in

    def set_tx_gain_in(self, tx_gain_in):
        self.tx_gain_in = tx_gain_in
        self.set_tx_gain(self.tx_gain_in)

    def get_tx_gain(self):
        return self.tx_gain

    def set_tx_gain(self, tx_gain):
        self.tx_gain = tx_gain
        self.bladeRF_sink_0.set_gain(self.tx_gain, 0)
        self.bladeRF_sink_0.set_if_gain(self.tx_gain, 0)

    def get_input_sigmf_entry(self):
        return self.input_sigmf_entry

    def set_input_sigmf_entry(self, input_sigmf_entry):
        self.input_sigmf_entry = input_sigmf_entry
        Qt.QMetaObject.invokeMethod(self._input_sigmf_entry_line_edit, "setText", Qt.Q_ARG("QString", str(self.input_sigmf_entry)))
        self.blocks_sigmf_source_minimal_0.open(self.input_sigmf_entry, True)

    def get_freq_tx(self):
        return self.freq_tx

    def set_freq_tx(self, freq_tx):
        self.freq_tx = freq_tx
        Qt.QMetaObject.invokeMethod(self._freq_tx_line_edit, "setText", Qt.Q_ARG("QString", eng_notation.num_to_str(self.freq_tx)))
        self.bladeRF_sink_0.set_center_freq(self.freq_tx, 0)



def argument_parser():
    description = 'Default to TCH filepath with test data Fs'
    parser = ArgumentParser(description=description)
    parser.add_argument(
        "--fc", dest="fc", type=eng_float, default=eng_notation.num_to_str(float(937e6)),
        help="Set fc [default=%(default)r]")
    parser.add_argument(
        "-i", "--input-file-name", dest="input_file_name", type=str, default='../test_data/gsm_test_voice_call.sigmf-data',
        help="Set input_file_name [default=%(default)r]")
    parser.add_argument(
        "--samp-rate", dest="samp_rate", type=eng_float, default=eng_notation.num_to_str(float((100e6/174))),
        help="Set fs [default=%(default)r]")
    parser.add_argument(
        "-s", "--serial-id", dest="serial_id", type=str, default="",
        help="Set serial [default=%(default)r]")
    parser.add_argument(
        "-g", "--tx-gain-in", dest="tx_gain_in", type=intx, default=16,
        help="Set gain [default=%(default)r]")
    return parser


def main(top_block_cls=transmit_tch_bladerf, options=None):
    if options is None:
        options = argument_parser().parse_args()

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls(fc=options.fc, input_file_name=options.input_file_name, samp_rate=options.samp_rate, serial_id=options.serial_id, tx_gain_in=options.tx_gain_in)

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
