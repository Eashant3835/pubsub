# DESIGN DESCISIONS

## read_entry paramaters
Problem: What are the parameters of read_entry?

Alternative: topic and offset

Choice: path, starts and offset

Tradeoffs: The starts of a different topic being sent results in two cases: Either it lands on a boundary like 0, and the offset works so the consumer wouldn't know, or it doesn't land on one, and the broker starts reading mid file - which will certainly cause a LogCorruptionError. The error is also misleading since the file is completely fine.

Reason: read_entry does not have to rely on the global indexes variable. Global variables are easily mutatable so its not reliable.

## store_message ordering
Problem: Does store_message append to the index before or after the fsync?

Alternative: Before the fsync

Choice: After the fsync

Tradeoffs: Only works if fsync is fully synchronous

Reasons: This way it offers the consumer a guarantee that anything thats in the index is stored.

## Eager indexing
Problem/Decision: When should the broker scan for indexes?

Alternative: Lazy indexing, broker getting the index for a topic after a consumer requested a message for it

Choice: Eager indexing, scan for all indexes at startup

Tradeoffs: The broker is unavailable for longer after a startup, and the startup time scales with log size, and one bad log can cause startup to halt because recover raises a LogCorruptionError

Reason: This way, after the initial startup wait, consumers do not have to wait to receive messages

## recover passing starts
Problem: Does recover pass through starts?

Alternative: There are 2 alternative:
Either you call only scan, which means the file does not get repaired
or
You call recover, then scan, which means every file is read and checksummed twice at startup

Choice: It does pass through starts

Tradeoff: A function that does repair, also does indexing

Reason: It allows for the file to be repaired and get the index from it, with every file being read and checksummed once at startup

