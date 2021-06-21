import sys

from agents.alpha0.utils import *
import argparse
import tensorflow
from keras.models import Model
from keras.layers import (Conv2D, Flatten, Dropout, Dense, concatenate, BatchNormalization, Reshape, Activation, Input )
from keras.optimizers import *

from engine.board import ML_BOARD_FEATURES

class CarcassoneNNet():

    def __init__(self, game, args):
        # game params
        self.board_x, self.board_y = game.getBoardSize()
        self.action_size = game.getActionSize()
        self.args = args

        # Neural Net
        ##
        ## <= TODO: Why nchannels at start ? Look at this
        input_boards = Input(shape=(self.board_x, self.board_y, ML_BOARD_FEATURES))    # s: batch_size x board_x x board_y
        input_aux = Input(shape=(game.getAuxInputSize(),))

        x_image = Reshape((self.board_x, self.board_y, ML_BOARD_FEATURES))(input_boards)                # batch_size  x board_x x board_y x 1
        h_conv1 = Activation('relu')(BatchNormalization(axis=3)(Conv2D(args.num_channels, 3, padding='same', use_bias=False)(x_image)))         # batch_size  x board_x x board_y x num_channels
        h_conv2 = Activation('relu')(BatchNormalization(axis=3)(Conv2D(args.num_channels, 3, padding='same', use_bias=False)(h_conv1)))         # batch_size  x board_x x board_y x num_channels
        h_conv3 = Activation('relu')(BatchNormalization(axis=3)(Conv2D(args.num_channels, 3, padding='same', use_bias=False)(h_conv2)))         # batch_size  x board_x x board_y x num_channels
        h_conv4 = Activation('relu')(BatchNormalization(axis=3)(Conv2D(args.num_channels, 3, padding='valid', use_bias=False)(h_conv3)))        # batch_size  x (board_x-2) x (board_y-2) x num_channels
        h_conv5 = Activation('relu')(BatchNormalization(axis=3)(Conv2D(args.num_channels, 3, padding='valid', use_bias=False)(h_conv4)))        # batch_size  x (board_x-2) x (board_y-2) x num_channels
        h_conv6 = Activation('relu')(BatchNormalization(axis=3)(Conv2D(args.num_channels, 3, padding='valid', use_bias=False)(h_conv5)))        # batch_size  x (board_x-4) x (board_y-4) x num_channels
        h_conv7_flat = Flatten()(h_conv5)


        ######
        # !!!!
        # >>>> Merging AUX Features after conv layers
        # !!!!
        h_conv7_flat_concat = concatenate([h_conv7_flat, input_aux])

        s_fc1 = Dropout(args.dropout)(Activation('relu')(BatchNormalization(axis=1)(Dense(1024, use_bias=False)(h_conv7_flat_concat))))  # batch_size x 1024

        s_fc2 = Dropout(args.dropout)(Activation('relu')(
            BatchNormalization(axis=1)(Dense(1024, use_bias=False)(s_fc1))))  # batch_size x 1024

        s_fc3 = Dropout(args.dropout)(Activation('relu')(BatchNormalization(axis=1)(Dense(512, use_bias=False)(s_fc2))))                 # batch_size x 512
        self.pi = Dense(self.action_size, activation='softmax', name='pi')(s_fc3)   # batch_size x self.action_size
        self.v = Dense(1, activation='tanh', name='v')(s_fc3)                       # batch_size x 1

        self.model = Model(inputs=[input_boards, input_aux], outputs=[self.pi, self.v])
        self.model.compile(loss=['categorical_crossentropy', 'mean_squared_error'], optimizer=Adam(args.lr))


    def OLD(self, game, args):
        # game params
        self.board_x, self.board_y = game.getBoardSize()
        self.action_size = game.getActionSize()
        self.args = args

        # Neural Net
        ##
        ## <= TODO: Why nchannels at start ? Look at this
        input_boards = Input(shape=(self.board_x, self.board_y, ML_BOARD_FEATURES))    # s: batch_size x board_x x board_y
        input_aux = Input(shape=(game.getAuxInputSize(),))

        x_image = Reshape((self.board_x, self.board_y, ML_BOARD_FEATURES))(input_boards)                # batch_size  x board_x x board_y x 1
        h_conv1 = Activation('relu')(BatchNormalization(axis=3)(Conv2D(args.num_channels, 3, padding='same', use_bias=False)(x_image)))         # batch_size  x board_x x board_y x num_channels
        h_conv2 = Activation('relu')(BatchNormalization(axis=3)(Conv2D(args.num_channels, 3, padding='same', use_bias=False)(h_conv1)))         # batch_size  x board_x x board_y x num_channels
        h_conv3 = Activation('relu')(BatchNormalization(axis=3)(Conv2D(args.num_channels, 3, padding='same', use_bias=False)(h_conv2)))         # batch_size  x board_x x board_y x num_channels
        h_conv4 = Activation('relu')(BatchNormalization(axis=3)(Conv2D(args.num_channels, 3, padding='valid', use_bias=False)(h_conv3)))        # batch_size  x (board_x-2) x (board_y-2) x num_channels
        h_conv5 = Activation('relu')(BatchNormalization(axis=3)(Conv2D(args.num_channels, 3, padding='valid', use_bias=False)(h_conv4)))        # batch_size  x (board_x-2) x (board_y-2) x num_channels
        h_conv6 = Activation('relu')(BatchNormalization(axis=3)(Conv2D(args.num_channels, 3, padding='valid', use_bias=False)(h_conv5)))        # batch_size  x (board_x-4) x (board_y-4) x num_channels
        h_conv7_flat = Flatten()(h_conv5)


        ######
        # !!!!
        # >>>> Merging AUX Features after conv layers
        # !!!!
        h_conv7_flat_concat = concatenate([h_conv7_flat, input_aux])

        s_fc1 = Dropout(args.dropout)(Activation('relu')(BatchNormalization(axis=1)(Dense(1024, use_bias=False)(h_conv7_flat_concat))))  # batch_size x 1024

        s_fc2 = Dropout(args.dropout)(Activation('relu')(
            BatchNormalization(axis=1)(Dense(1024, use_bias=False)(s_fc1))))  # batch_size x 1024

        s_fc3 = Dropout(args.dropout)(Activation('relu')(BatchNormalization(axis=1)(Dense(512, use_bias=False)(s_fc2))))                 # batch_size x 512
        self.pi = Dense(self.action_size, activation='softmax', name='pi')(s_fc3)   # batch_size x self.action_size
        self.v = Dense(1, activation='tanh', name='v')(s_fc3)                       # batch_size x 1

        self.model = Model(inputs=[input_boards, input_aux], outputs=[self.pi, self.v])
        self.model.compile(loss=['categorical_crossentropy', 'mean_squared_error'], optimizer=Adam(args.lr))