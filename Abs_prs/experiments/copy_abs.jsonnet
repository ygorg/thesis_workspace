local root = "/home/gallina/data/datasets/KP20k/abs/";
# local tg_ns = "ref";
{
  # Datasets
  train_data_path: root + "kp20k.train.json.part*",
  validation_data_path: root + "kp20k.valid.json",

  dataset_reader: {
    type: "multiprocess",
    num_workers: 4,
    base_reader: {
    type: "kp20k_copy",
    target_namespace: 'tokens',
    token_indexers: {'tokens': {namespace: 'tokens', lowercase_tokens: true}},
    #ref_token_indexers: {'ref': {namespace: tg_ns', lowercase_tokens: true}},  # Do not share vocabulary
    tokenizer: {word_splitter: 'nltk'},
    add_start_token: true,
    ref_max_token: 10,
    #filter_reference: true,
    lazy: true,
    }
  },

  validation_dataset_reader: $.dataset_reader.base_reader {type: 'kp20k_copy'},

  datasets_for_vocab_creation: ['train'],
  vocabulary: {
    max_vocab_size: 50000,
    tokens_to_add: {
      tokens: ['@@digit@@'],
      ref: ['@@digit@@']
    },
  },

  # Training
  iterator: {
    type: "bucket",
    sorting_keys: [["source_tokens", "num_tokens"]],
    batch_size: 32,
  },
  validation_iterator: $.iterator {batch_size: 8},
  trainer: {
    cuda_device: 0,
    num_epochs: 40,
    patience: 8,

    grad_clipping: 0.1,
    optimizer: {
      type: "adam",
      lr: 0.0001,
    },
  },

  model: {
    type: "seq2seq_copy",
    max_decoding_steps: 6,  # Use this value if there is no target, else use the length of the target
    attention: {type: 'linear', tensor_1_dim: $.model.encoder.hidden_size * $.model.encoder.num_layers, tensor_2_dim: $.model.encoder.hidden_size * $.model.encoder.num_layers},
    # scheduled_sampling_ratio: 0.4,  # eq. teacher forcing
    beam_size: 50,  # used at prediction time
    filter_output: true,  # Remove prediction containing OOV or PAD
    target_namespace: 'tokens',
    #target_namespace: tg_ns',
    source_embedder: {
      tokens: {
        type: "embedding",
        embedding_dim: 150,
        trainable: true,
      }
    },
    #target_embedder: $.model.source_embedder.tokens {
    #  embedding_dim: 150, vocab_namespace: $.model.target_namespace,
    #},
    encoder: {
      type: "gru",
      bidirectional: true,
      input_size: $.model.source_embedder.tokens.embedding_dim,
      hidden_size: 300,
      num_layers: 2,
      dropout: 0.5,
    },
    decoder_cell: "gru",
    text_based_metrics: [{type: 'f1_kp', rank: 5}, {type: 'f1_kp', rank: 10}]
  }
}
