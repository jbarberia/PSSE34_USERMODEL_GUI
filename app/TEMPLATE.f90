SUBROUTINE %model_name%(%parameters%)

    INCLUDE 'COMON4.INS'
    INTEGER %%
    REAL %%

    J = %index_call_1% ! STARTING 'CON'
    K = %index_call_2% ! STARTING 'STATE'
    L = %index_call_3% ! STARTING 'VAR'
    M = %index_call_4% ! STARTING 'ICON'

    IF (MIDTRM) RETURN


    SELECT CASE(MODE)
    CASE(1) ! INCIALIZACION
        %mode_1%
    CASE(2) ! CALCULO DE DERIVADAS
        %mode_2%
    CASE(3) ! CALCULO DE LAS SALIDAS
        %mode_3%
    CASE(4) ! ESPACIOS PARA INTEGRACION
        NINTEG=MAX(NINTEG, K+1)
    CASE(5)
    CASE(6)
    CASE(7)
    CASE(8) ! DESCRIPCION DE LOS CONS
        %mode_8%
    

    END SELECT
END SUBROUTINE
