# Copied & modified from https://www.dacon.io/competitions/official/235757/codeshare/3244?page=1&dtype=recent


import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


def get_sinusoid_encoding_table(n_seq, hidn):
    
    def cal_angle(position, i_hidn):
        return position / np.power(10000, 2 * (i_hidn // 2) / hidn)

    def get_posi_angle_vec(position):
        return [cal_angle(position, i_hidn) for i_hidn in range(hidn)]
    
    sinusoid_table = np.array([get_posi_angle_vec(i_seq) for i_seq in range(n_seq)])
    sinusoid_table[:, 0::2] = np.sin(sinusoid_table[:, 0::2])  # even index sin
    sinusoid_table[:, 1::2] = np.cos(sinusoid_table[:, 1::2])  # odd index cos

    return sinusoid_table


def get_attn_decoder_mask(seq):
    batch, window_size, d_hidn = seq.size()
    subsequent_mask = torch.ones((batch, window_size, window_size), device=seq.device)
    subsequent_mask = subsequent_mask.triu(diagonal=1)
    return subsequent_mask


class scaled_dot_product_attention(nn.Module):
    def __init__(self, args):
        super().__init__()
        self.args = args
        self.dropout = nn.Dropout(self.args.dropout)
        self.scale = 1 / (self.args.d_head ** 0.5)

    def forward(self, q, k, v, attn_mask=False):
        scores = torch.matmul(q, k.transpose(-1, -2))
        scores = scores.mul_(self.scale)

        if attn_mask is not False:
            scores.masked_fill_(attn_mask, -1e9)
            attn_prob = nn.Softmax(dim=-1)(scores)
            attn_prob = self.dropout(attn_prob)
            context = torch.matmul(attn_prob, v)
        else:
            attn_prob = nn.Softmax(dim=-1)(scores)
            attn_prob = self.dropout(attn_prob)
            context = torch.matmul(attn_prob, v)
    
        return context, attn_prob


class multihead_attention(nn.Module):
    def __init__(self, args):
        super().__init__()
        self.args = args
        self.W_Q = nn.Linear(self.args.d_hidn, self.args.n_head * self.args.d_head)
        self.W_K = nn.Linear(self.args.d_hidn, self.args.n_head * self.args.d_head)
        self.W_V = nn.Linear(self.args.d_hidn, self.args.n_head * self.args.d_head)

        self.scaled_dot_attn = scaled_dot_product_attention(self.args)
        self.linear = nn.Linear(self.args.n_head * self.args.d_head, self.args.d_hidn)
        self.dropout = nn.Dropout(self.args.dropout)
    
    def forward(self, q, k, v, attn_mask=False):
        batch_size = q.size(0)
        q_s = self.W_Q(q).view(batch_size, -1, self.args.n_head, self.args.d_head).transpose(1, 2)
        k_s = self.W_K(k).view(batch_size, -1, self.args.n_head, self.args.d_head).transpose(1, 2)
        v_s = self.W_V(v).view(batch_size, -1, self.args.n_head, self.args.d_head).transpose(1, 2)

        if attn_mask is not False:
            attn_mask = attn_mask.unsqueeze(1).repeat(1, self.args.n_head, 1, 1)
            context, attn_prob = self.scaled_dot_attn(q_s, k_s, v_s, attn_mask)
        else:
            context, attn_prob = self.scaled_dot_attn(q_s, k_s, v_s)
        context = context.transpose(1, 2).contiguous().view(batch_size, -1, self.args.n_head * self.args.d_head)

        output = self.linear(context)
        output = self.dropout(output)

        return output, attn_prob


class poswise_feedforward_net(nn.Module):
    def __init__(self, args):
        super().__init__()
        self.args = args
        self.conv1 = nn.Conv1d(in_channels=self.args.d_hidn, out_channels=self.args.d_ff, kernel_size=1)
        self.conv2 = nn.Conv1d(in_channels=self.args.d_ff, out_channels=self.args.d_hidn, kernel_size=1)
        self.active = F.gelu
        self.dropout = nn.Dropout(self.args.dropout)

    def forward(self, inputs):
        output = self.conv1(inputs.transpose(1, 2).contiguous())
        output = self.active(output)
        output = self.conv2(output).transpose(1, 2).contiguous()
        output = self.dropout(output)

        return output

class encoderlayer(nn.Module):
    def __init__(self, args):
        super().__init__()
        self.args = args
        self.self_attn = multihead_attention(self.args)
        self.pos_ffn = poswise_feedforward_net(self.args)

    def forward(self, inputs):
        att_outputs, attn_prob = self.self_attn(inputs, inputs, inputs)
        att_outputs = att_outputs + inputs

        ffn_outputs = self.pos_ffn(att_outputs)
        ffn_outputs = ffn_outputs + att_outputs

        return ffn_outputs, attn_prob


class encoder(nn.Module):
    def __init__(self, args):
        super().__init__()
        self.args = args
        self.enc_emb = nn.Linear(in_features=self.args.window_size, out_features=self.args.d_hidn, bias=False)
        sinusoid_table = torch.FloatTensor(get_sinusoid_encoding_table(self.args.e_features, self.args.d_hidn))
        self.pos_emb = nn.Embedding.from_pretrained(sinusoid_table, freeze=True)
        self.layers = nn.ModuleList([encoderlayer(self.args) for _ in range(self.args.n_layer)])
        self.enc_attn_probs = None

    def forward(self, inputs):  # inputs.shape = (batch_size, window_size, n_features)  ex) (128, 10 , 4)
        self.enc_attn_probs = []
        positions = torch.arange(inputs.size(2), device=inputs.device).expand(inputs.size(0), inputs.size(2)).contiguous()  # (batch_size, n_features)  ex) (128, 4)
        outputs = self.enc_emb(inputs.transpose(2, 1).contiguous()) + self.pos_emb(positions)  # (batch_size, n_features, n_hidn)  ex) (128, 4, 256)

        for layer in self.layers:
            outputs, enc_attn_prob = layer(outputs)
            self.enc_attn_probs.append(enc_attn_prob)

        return outputs

    
class decoderlayer(nn.Module):
    def __init__(self, args):
        super().__init__()
        self.args = args
        self.self_attn = multihead_attention(self.args)
        self.dec_enc_attn = multihead_attention(self.args)
        self.pos_ffn = poswise_feedforward_net(self.args)

    def forward(self, dec_inputs, enc_outputs, attn_mask):
        self_att_outputs, dec_attn_prob = self.self_attn(dec_inputs, dec_inputs, dec_inputs, attn_mask)
        self_att_outputs = self_att_outputs + dec_inputs

        dec_enc_att_outputs, dec_enc_attn_prob = self.dec_enc_attn(self_att_outputs, enc_outputs, enc_outputs)
        dec_enc_att_outputs = dec_enc_att_outputs + self_att_outputs
        
        ffn_outputs = self.pos_ffn(dec_enc_att_outputs)
        ffn_outputs = ffn_outputs + dec_enc_att_outputs

        return ffn_outputs, dec_attn_prob, dec_enc_attn_prob



class decoder(nn.Module):
    def __init__(self, args):
        super().__init__()
        self.args = args
        self.dec_emb = nn.Linear(in_features=self.args.d_features, out_features=self.args.d_hidn, bias=False)
        sinusoid_table = torch.FloatTensor(get_sinusoid_encoding_table(self.args.window_size , self.args.d_hidn))
        self.pos_emb = nn.Embedding.from_pretrained(sinusoid_table, freeze=True)
        self.layers = nn.ModuleList([decoderlayer(self.args) for _ in range(self.args.n_layer)])
        self.dec_attn_probs = None
        self.dec_enc_attn_probs = None

    def forward(self, dec_inputs, enc_outputs):
        self.dec_attn_probs = []  
        self.dec_enc_attn_probs = []
        positions = torch.arange(dec_inputs.size(1), device=dec_inputs.device).expand(dec_inputs.size(0), dec_inputs.size(1)).contiguous()
        dec_output = self.dec_emb(dec_inputs) + self.pos_emb(positions)
        
        attn_mask = torch.gt(get_attn_decoder_mask(dec_inputs), 0)

        for layer in self.layers:
            dec_outputs, dec_attn_prob, dec_enc_attn_prob = layer(dec_output, enc_outputs, attn_mask)
            self.dec_attn_probs.append(dec_attn_prob)
            self.dec_enc_attn_probs.append(dec_enc_attn_prob)
        
        return dec_outputs


class TimeDistributed(nn.Module):
    def __init__(self, module):
        super(TimeDistributed, self).__init__()
        self.module = module

    def forward(self, x):

        if len(x.size()) <= 2:  # (batch_size, window_size * d_hidn)  ex) (128, 2560)
            return self.module(x)
        
        x_reshape = x.contiguous().view(-1, x.size(-1))  # (samples * timesteps, input_size)
        y = self.module(x_reshape)

        if len(x.size()) == 3:
            y = y.contiguous().view(x.size(0), -1, y.size(-1))

        return y


class transformer(nn.Module):
    def __init__(self, args):
        super().__init__()
        self.args = args
        self.encoder = encoder(self.args)
        self.decoder = decoder(self.args)
        self.fc1 = TimeDistributed(nn.Linear(in_features=self.args.window_size*self.args.d_hidn, out_features=self.args.dense_h))
        self.fc2 = TimeDistributed(nn.Linear(in_features=self.args.dense_h, out_features=self.args.ahead * self.args.output_size))
        self.activation = nn.SELU()

    def forward(self, enc_inputs, dec_inputs):
        enc_outputs = self.encoder(enc_inputs)  # (batch_size, n_features, d_hidn)  ex) (128, 4, 256)
        dec_outputs = self.decoder(dec_inputs, enc_outputs)  # (batch_size, window_size, d_hidn)  ex) (128, 10, 256)
        
        # dec_outputs.view(dec_outputs.size(0), -1).shape = (batch_size, window_size * d_hidn)  ex) (128, 2560)
        dec_outputs = self.fc1(dec_outputs.view(dec_outputs.size(0), -1))  # (batch_size, dense_h)   ex) (128, 128)
        dec_outputs = self.activation(dec_outputs)
        dec_outputs = self.fc2(dec_outputs)  # (batch_size, ahead * output_size)  ex) (128, 8)                
        dec_outputs = dec_outputs.view(dec_outputs.size(0), self.args.ahead, self.args.output_size)  #  ex) (128, 2, 4)

        return dec_outputs