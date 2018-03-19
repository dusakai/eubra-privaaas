package br.unicamp.ft.arx.service;
import org.deidentifier.arx.*;
import org.deidentifier.arx.aggregates.HierarchyBuilderRedactionBased;
import org.deidentifier.arx.aggregates.HierarchyBuilderRedactionBased.Order;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.nio.charset.Charset;
import java.util.StringTokenizer;
import org.deidentifier.arx.AttributeType.MicroAggregationFunction;
import org.deidentifier.arx.DataType;
import java.io.FileInputStream;
import java.io.InputStreamReader;
import java.io.LineNumberReader;
import java.nio.charset.StandardCharsets;
import java.io.IOException;
import java.util.Arrays;
//import org.apache.commons.io.FilenameUtils;
import org.deidentifier.arx.criteria.KAnonymity;
import org.deidentifier.arx.ARXAnonymizer;
import org.deidentifier.arx.ARXConfiguration;
import org.deidentifier.arx.ARXLattice.ARXNode;
import org.deidentifier.arx.ARXResult;
import org.deidentifier.arx.AttributeType.Hierarchy;
import org.deidentifier.arx.Data;
/**
 *
 */
public class Anonymizer extends ServiceArx {
     private static double RR1;
     private static int contline;
    private static double Rmax;
    public static void main(String[] args) throws IOException {
       
        String Dataset = args[0];
        String Policy = args [1];
        String saveIn = args[2];
        int K = 2;     
     
        
        //String absolutpath =  Dataset.getCanonicalPath();
        //int indexFile = Dataset.indexOf("arx-poc");
        
           
      
        // String relativepath = Dataset.substring(0, indexFile); //+ "_anonymized.csv";
         
        // int indexFile2 = pathRelative.indexOf("dist")+1;
         //String path = pathRelative.substring(0, (indexFile2));
       
           LineNumberReader lineCounter = new LineNumberReader(new InputStreamReader(new FileInputStream(Dataset)));
           String nextLine =null;
            try {
			while ((nextLine = lineCounter.readLine()) != null) {
                                                  
                          if (nextLine == null)
                              break;
            }
                        setContline(lineCounter.getLineNumber());
                      
                                   				} catch (IOException done) {
		}
     
        DataSource source = DataSource.createCSVSource(Dataset, Charset.forName("UTF-8"), ';', true);
       
            try {
            FileReader reader = new FileReader(Policy); // Localização do Arquivo
            BufferedReader leitor = new BufferedReader(reader);
            StringTokenizer st = null;
            String line = null;
            String field; // Armazena campo de numero
            String classdata;// Armazena campo de matricula
            while ((line = leitor.readLine()) != null) {
                //UTILIZA DELIMITADOR ; PARA DIVIDIR OS CAMPOS
                st = new StringTokenizer(line, ";");
                String dados = null;
                while (st.hasMoreTokens()) {
                    // Field Label
                    dados = st.nextToken();
                    field = dados;
                    if (field.equals("Rmax")){                	 
                    Rmax = Double.parseDouble(st.nextToken());
                   
                      } else 
                      {
                    // Field Data Classification
                    dados = st.nextToken();
                    classdata = dados;
                    source.addColumn(field, DataType.STRING);
                    
                }}
            }
                //    leitor.close();
               //     reader.close();
        } catch (
                IOException | NumberFormatException e)

        {
        }

        Data data = Data.create(source);
        

        try

        {
            FileReader reader1 = new FileReader(Policy); // Localização do Arquivo
            BufferedReader leitor1 = new BufferedReader(reader1);
            StringTokenizer st1 = null;
            String linha1 = null;
            String field1; // Armazena campo de numero
            String classdata1;// Armazena campo de matricula
            while ((linha1 = leitor1.readLine()) != null) {
                //UTILIZA DELIMITADOR ; PARA DIVIDIR OS CAMPOS
                st1 = new StringTokenizer(linha1, ";");
                String dados1 = null;
                             
                while (st1.hasMoreTokens()) {
                                        
                    // Field Label
                    dados1 = st1.nextToken();
                    field1 = dados1;
                     if (field1.equals("Rmax")){                	 
                    Rmax = Double.parseDouble(st1.nextToken());
                 
                      } else {
                                     
                    // Field Data Classification
                    dados1 = st1.nextToken();
                    classdata1 = dados1;
                    //load Hierarchy Builder
                     //HierarchyBuilderRedactionBased<?> supressing1 = HierarchyBuilderRedactionBased.create(Order.LEFT_TO_RIGHT,
                             //   Order.LEFT_TO_RIGHT,Character.MIN_VALUE,Character.MAX_VALUE);
                    HierarchyBuilderRedactionBased<?> supressing1 = HierarchyBuilderRedactionBased.create(Order.LEFT_TO_RIGHT,
                            Order.LEFT_TO_RIGHT,' ','*');
                    
                    HierarchyBuilderRedactionBased<?> supressing2 = HierarchyBuilderRedactionBased.create(Order.RIGHT_TO_LEFT,
                            Order.RIGHT_TO_LEFT,' ','*');
                  
                    if (classdata1.equals("1")) {
                        data.getDefinition().setAttributeType(field1, AttributeType.INSENSITIVE_ATTRIBUTE);
                    }
                    if (classdata1.equals("2")) {
                        data.getDefinition().setAttributeType(field1, AttributeType.IDENTIFYING_ATTRIBUTE);
                    }
                    if (classdata1.equals("3")) {
                        data.getDefinition().setAttributeType(field1, AttributeType.QUASI_IDENTIFYING_ATTRIBUTE);
                        data.getDefinition().setMicroAggregationFunction(field1, MicroAggregationFunction.createGeneralization());

                    }
                    if (classdata1.equals("4")) {
                        data.getDefinition().setAttributeType(field1, AttributeType.IDENTIFYING_ATTRIBUTE);
                    }
                    if (classdata1.equals("SR")) {
                       data.getDefinition().setAttributeType(field1, AttributeType.QUASI_IDENTIFYING_ATTRIBUTE);
                        data.getDefinition().setAttributeType(field1, supressing1);
                    }
                    if (classdata1.equals("SL")) {
                       data.getDefinition().setAttributeType(field1, AttributeType.QUASI_IDENTIFYING_ATTRIBUTE);
                        data.getDefinition().setAttributeType(field1, supressing2);
                    }
                    if (classdata1.equals("DT")) {
                        data.getDefinition().setAttributeType(field1, Hierarchy.create("arx-poc"+File.separator +"hierarchy"+ File.separator +"birthdate.csv", StandardCharsets.UTF_8, ';'));     
                    }
                    if (classdata1.equals("AG")) {
                             data.getDefinition().setAttributeType(field1, Hierarchy.create("arx-poc"+File.separator +"hierarchy"+ File.separator +"age.csv", StandardCharsets.UTF_8, ';'));
                                                      
                   }
            }}
    
        }
            // leitor1.close();
               //     reader1.close(); 
        } catch (
                IOException | NumberFormatException e)

        {
        }
        ARXPopulationModel populationmodel = ARXPopulationModel.create(data.getHandle().getNumRows(), 0.01d);


        // Create an instance of the anonymizer
        ARXAnonymizer anonymizer = new ARXAnonymizer();
        ARXConfiguration config = ARXConfiguration.create();
        config.addPrivacyModel(new KAnonymity(K));
        config.setMaxOutliers(0d);
        
        ARXResult result = anonymizer.anonymize(data, config);
        ARXNode node = result.getGlobalOptimum();
        
        setRR1(result.getOutput().getRiskEstimator(populationmodel).getSampleBasedReidentificationRisk().getEstimatedProsecutorRisk());
        
        //if setRR1 = null { VocÊ precisa especificar pelomenos 1 quasi-identifier com generalização SR ou SL)
                
        while (getRR1() >= Rmax) {

            source = DataSource.createCSVSource(Dataset, Charset.forName("UTF-8"), ';', true);
            try {
                FileReader reader2 = new FileReader(Policy); // Localização do Arquivo
                BufferedReader leitor2 = new BufferedReader(reader2);
                StringTokenizer st2 = null;
                String line2 = null;
                String field2; // Armazena campo de numero
                String classdata2;// Armazena campo de matricula
                while ((line2 = leitor2.readLine()) != null) {
                    //UTILIZA DELIMITADOR ; PARA DIVIDIR OS CAMPOS
                    st2 = new StringTokenizer(line2, ";");
                    String dados2 = null;
                    while (st2.hasMoreTokens()) {
                        // Field Label
                        dados2 = st2.nextToken();
                        field2 = dados2;
                        
                            if (field2.equals("Rmax")){                	 
                            Rmax = Double.parseDouble(st2.nextToken());
                           
                            } else {
                        // Field Data Classification
                            dados2 = st2.nextToken();
                            classdata2 = dados2;
                            source.addColumn(field2, DataType.STRING);
                                    }
                    }       }
                // leitor2.close();
               //  reader2.close();
            } catch (
                IOException | NumberFormatException e)

        {
        }

            data = Data.create(source);

            try

            {
                FileReader reader3 = new FileReader(Policy); // Localização do Arquivo
                BufferedReader leitor3 = new BufferedReader(reader3);
                StringTokenizer st3 = null;
                String linha3 = null;
                String field3; // Armazena campo de numero
                String classdata3;// Armazena campo de matricula
                while ((linha3 = leitor3.readLine()) != null) {
                    //UTILIZA DELIMITADOR ; PARA DIVIDIR OS CAMPOS
                    st3 = new StringTokenizer(linha3, ";");
                    String dados3 = null;
                    while (st3.hasMoreTokens()) {
                        // Field Label
                        dados3 = st3.nextToken();
                        field3 = dados3;
                        if (field3.equals("Rmax")){                	 
                         Rmax = Double.parseDouble(st3.nextToken());
                         } else {
                        // Field Data Classification
                        dados3 = st3.nextToken();
                        classdata3 = dados3;
                        //load Hierarchy Builder
                        HierarchyBuilderRedactionBased<?> supressing1 = HierarchyBuilderRedactionBased.create(Order.LEFT_TO_RIGHT,
                                Order.LEFT_TO_RIGHT,' ','*');
                        
                        HierarchyBuilderRedactionBased<?> supressing2 = HierarchyBuilderRedactionBased.create(Order.RIGHT_TO_LEFT,
                                Order.RIGHT_TO_LEFT,
                                ' ',
                                '*');
                        if (classdata3.equals("1")) {
                            data.getDefinition().setAttributeType(field3, AttributeType.INSENSITIVE_ATTRIBUTE);
                        }
                        if (classdata3.equals("2")) {
                            data.getDefinition().setAttributeType(field3, AttributeType.IDENTIFYING_ATTRIBUTE);
                        }
                        if (classdata3.equals("3")) {
                            data.getDefinition().setAttributeType(field3, AttributeType.QUASI_IDENTIFYING_ATTRIBUTE);
                            data.getDefinition().setMicroAggregationFunction(field3, MicroAggregationFunction.createGeneralization());
                        }
                        if (classdata3.equals("4")) {
                            data.getDefinition().setAttributeType(field3, AttributeType.IDENTIFYING_ATTRIBUTE);
                        }
                        if (classdata3.equals("SR")) {
                            data.getDefinition().setAttributeType(field3, AttributeType.QUASI_IDENTIFYING_ATTRIBUTE);
                            data.getDefinition().setAttributeType(field3, supressing1);
                        }
                        if (classdata3.equals("SL")) {
                            data.getDefinition().setAttributeType(field3, AttributeType.QUASI_IDENTIFYING_ATTRIBUTE);
                            data.getDefinition().setAttributeType(field3, supressing2);
                                                }
                         if (classdata3.equals("DT")) {
                             data.getDefinition().setAttributeType(field3, Hierarchy.create("arx-poc"+File.separator +"hierarchy"+ File.separator + "birthdate.csv", StandardCharsets.UTF_8, ';'));
                           
                    }
                               if (classdata3.equals("AG")) {
                           data.getDefinition().setAttributeType(field3, Hierarchy.create("arx-poc"+File.separator +"hierarchy"+ File.separator + "age.csv", StandardCharsets.UTF_8, ';'));
                  }
                        }
                }}
               //   leitor3.close();
                 //   reader3.close();
                } catch (IOException | NumberFormatException e)

        {
        }
            populationmodel = ARXPopulationModel.create(data.getHandle().getNumRows(), 0.01d);

            // Create an instance of the anonymizer
            anonymizer = new ARXAnonymizer();
            config = ARXConfiguration.create();
            config.addPrivacyModel(new KAnonymity((K++)));
            config.setMaxOutliers(0d);
            result = anonymizer.anonymize(data, config);
            
            
             if (getContline()<= K){
             System.out.println("It is not possible to implement the risk requested. You Need specify new threshold or add more records to the dataset"); 
             System.exit(0); // Tratamento de erro ponto de execução nula... k maior que o dataset
           
           }
            setRR1(result.getOutput().getRiskEstimator(populationmodel).getSampleBasedReidentificationRisk().getEstimatedProsecutorRisk());
          
    
        }
            System.out.println("- Writing data...");
            //Iterator<String[]> transformed = result.getOutput(false).iterator();

            // Perform risk analysis
            System.out.println("- Output data");
            //print(result.getOutput());
            System.out.println("\n- Mixed risks");
            System.out.println("  * Prosecutor re-identification risk: " + result.getOutput().getRiskEstimator(populationmodel).getSampleBasedReidentificationRisk().getEstimatedProsecutorRisk());
            System.out.println("  * Journalist re-identification risk: " + result.getOutput().getRiskEstimator(populationmodel).getSampleBasedReidentificationRisk().getEstimatedJournalistRisk());
            System.out.println("  * Marketer re-identification risk: " + result.getOutput().getRiskEstimator(populationmodel).getSampleBasedReidentificationRisk().getEstimatedMarketerRisk());
            System.out.println("  * K anonimity implementado: " + K);
            System.out.println(" - Information loss: " + result.getGlobalOptimum().getLowestScore() + " / " + result.getGlobalOptimum().getHighestScore());
            System.out.println(" - Statistics");
            System.out.println(result.getOutput(result.getGlobalOptimum(), false).getStatistics().getEquivalenceClassStatistics());
            System.out.println("Data: " + data.getHandle().getView().getNumRows() + " records with " + data.getDefinition().getQuasiIdentifyingAttributes().size() + " quasi-identifiers");
            System.out.println(" - Policies available: " + result.getLattice().getSize());
            System.out.println(" - Solution: " + Arrays.toString(node.getTransformation()));
            System.out.println("   * Optimal: " + result.getLattice().isComplete());
            System.out.println("   * Time needed: " + result.getTime() + "[ms]");
            System.out.print(" - Writing data...");
            result.getOutput(false).save(saveIn, ';');
            System.out.println("Done!");
        

        }

    public Anonymizer() {
    }

   
    /**
     * @return the RR1
     */
    public static double getRR1() {
        return RR1;
    }

    /**
     * @param aRR1 the RR1 to set
     */
    public static void setRR1(double aRR1) {
        RR1 = aRR1;
    }

    /**
     * @return the contline
     */
    public static int getContline() {
        return contline;
    }

    /**
     * @param aContline the contline to set
     */
    public static void setContline(int aContline) {
        contline = aContline;
    }

    private static int getcontline() {
        throw new UnsupportedOperationException("Not supported yet."); //To change body of generated methods, choose Tools | Templates.
    }

    private static void close() {
        throw new UnsupportedOperationException("Not supported yet."); //To change body of generated methods, choose Tools | Templates.
    }

    private static String readLine() {
        throw new UnsupportedOperationException("Not supported yet."); //To change body of generated methods, choose Tools | Templates.
    }

    private static String lineCounter() {
        throw new UnsupportedOperationException("Not supported yet."); //To change body of generated methods, choose Tools | Templates.
    }
}