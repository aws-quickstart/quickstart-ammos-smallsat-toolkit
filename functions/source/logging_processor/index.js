const zlib = require("zlib");
const aws_sdk = require("aws-sdk");

function transform(logEvent, owner, logGroup, logStream) {
    const source = buildSource(logEvent.message, logEvent.extractedFields);
    source["timestamp"] = new Date(1 * logEvent.timestamp).toISOString();
    source["id"] = logEvent.id;
    source["type"] = "CloudWatchLogs";
    source["@message"] = logEvent.message;
    source["@owner"] = owner;
    source["@log_group"] = logGroup;
    source["@log_stream"] = logStream;
    return source;
}

function buildSource(message, extractedFields) {
    if (extractedFields) {
        const source = {};
        for (const key in extractedFields) {
            if (Object.prototype.hasOwnProperty.call(extractedFields, key) &&
                extractedFields[key]) {
                const value = extractedFields[key];
                if (isNumeric(value)) {
                    source[key] = 1 * value;
                    continue;
                }
                const jsonSubString = extractJson(value);
                if (jsonSubString !== null) {
                    source["$" + key] = JSON.parse(jsonSubString);
                }
                source[key] = value;
            }
        }
        return source;
    }
    const jsonSubString = extractJson(message);
    if (jsonSubString !== null) {
        return JSON.parse(jsonSubString);
    }
    return {};
}
function extractJson(message) {
    const jsonStart = message.indexOf("{");
    if (jsonStart < 0)
        return null;
    const jsonSubString = message.substring(jsonStart);
    return isValidJson(jsonSubString) ? jsonSubString : null;
}
function isValidJson(message) {
    try {
        JSON.parse(message);
    }
    catch (e) {
        return false;
    }
    return true;
}
function isNumeric(n) {
    return !isNaN(parseFloat(n)) && isFinite(n);
}
function createRecordsFromEvents(logEvents, owner, logGroup, logStream) {
    const records = [];
    logEvents.forEach((event) => {
        const transformedEvent = transform(event, owner, logGroup, logStream);
        records.push({
            Data: zlib.gzipSync(Buffer.from(JSON.stringify(transformedEvent))),
        });
    });
    return records;
}

// https://stackoverflow.com/questions/40682103/splitting-an-array-up-into-chunks-of-a-given-size
function chunkArrayInGroups(arr, size) {
  var myArray = [];
  for(var i = 0; i < arr.length; i += size) {
    myArray.push(arr.slice(i, i+size));
  }
  return myArray;
}

async function putRecords(records, deliveryStreamName) {

    const firehose = new aws_sdk.Firehose();

    const recordChunks = chunkArrayInGroups(records, 500);

    for (const chunk of recordChunks) {
      const params = {
        DeliveryStreamName: deliveryStreamName,
        Records: chunk
      }
      await firehose.putRecordBatch(params).promise();
    };
}

exports.handler = async (event, context, callback) => {
  const output = await Promise.allSettled(event.records.map(async (r) => {
      const streamARN = event.deliveryStreamArn;
      const streamName = streamARN.split('/')[1];
      try {
          const buffer = Buffer.from(r.data, "base64");
          let decompressed;
          try {
              decompressed = zlib.gunzipSync(buffer);
          }
          catch (e) {
              throw new Error("error in decompressing data");
          }
          const payload = JSON.parse(decompressed);
          if (payload.messageType === "CONTROL_MESSAGE") {
              return;
          }
          else if (payload.messageType === "DATA_MESSAGE") {
              const records = createRecordsFromEvents(payload.logEvents, payload.owner, payload.logGroup, payload.logStream);
              await putRecords(records, streamName);

              // make sure to drop original batched CWL record
              return Promise.resolve({
                recordId: r.recordId,
                result: "Dropped"
              });

              // putRecords([{ recordId: r.recordId, result: "Dropped"}], streamName)
          }
          else {
              // if record is not compressed, this is the unbatched CWL uncompressed records
              return Promise.resolve({
                recordId: r.recordId,
                result: "Ok",
                data: Buffer.from(decompressed).toString("base64")
              });
          }
      }
      catch (e) {
        console.log('Error: ', e);
        callback(e, null);
      }
  }));

  let transformedRecords = [];
  for (const o of output) {
    if (o.status === "fulfilled") {
      transformedRecords.push(o.value);
    }
  }
  // console.log("transformedRecords");
  // console.log(transformedRecords)
  return callback(null, { records: transformedRecords });
};
