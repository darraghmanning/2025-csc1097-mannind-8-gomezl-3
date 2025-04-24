CALL apoc.load.json("file:///default.json") YIELD value AS data
WITH data
CREATE (s:Study {
  title: data.`Project Title`,
  sponsor: data.Sponsor,
  studyNumber: data.`Study Number`,
  protocolVersionAndDate: data.`Protocol Version and Date`,
  studyTitle: data.`Study Title`,
  phase: data.Phase,
  therapeuticArea: data.`Therapeutic Area`,
  numberOfPatients: data.`Number of Patients`,
  numberOfSites: data.`Number of Sites`,
  indication: data.Indication,
  treatmentDuration: data.`Duration of Treatment`,
  scheduleOfAssessments: data.`Schedule of Assessments`
})

WITH data, s
UNWIND data.questionnaires AS q
MERGE (qNode:Questionnaire {
  shortName: q.shortName
})
SET qNode.longName = q.longName,
    qNode.type = q.type,
    qNode.schedule = q.questionnaireSchedule

MERGE (s)-[:CONTAINS]->(qNode)