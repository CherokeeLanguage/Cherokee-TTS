https://github.com/Tomiinek/Multilingual_Text_to_Speech/issues/7

Oh, I see.

First, training on two languages does not make use of the model capabilities. The more languages you have, the more
information which can be shared across languages is present.

Second, you should have more speakers for each language (or you should have very similar voices for both mono-speaker
languages). The model has to learn the difference between language- and speaker- dependent information. However, there
is the multi-speaker VCTK dataset for English (a subset with a few speakers should be sufficient) and some Chinese
voices in my cleaned Common Voice data (see readme). You do not have to have a lot of examples for each speaker (50
transcript-recording pairs per speaker can be ok), but you should have more speakers with diverse voices (such as 10 or
20). If this is you case, just add these multi-speaker data to you actual dataset and it should be better.

Third, you should definitely reduce generator_dim to something like 2..4 and generator_bottleneck_dim should be lower
than this number, e.g., 1 or 2. Also speaker_embedding_dimension should be changed to roughly correspond to the number
of speakers you have. So if you have like 20 speakers, 16 or 32 ...

Finally, there is reversal_classifier_w which controls the weight of the adversarial speaker classifier's loss. This
parameter is really tricky. High values prevent the model from convergence, low values cause no effect. However, you
should first try to make your data multi-speaker.

https://github.com/Tomiinek/Multilingual_Text_to_Speech/issues/27

